import java.util.Vector;
import javax.microedition.lcdui.Canvas;
import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

/**
 * The main exploration state: map, entities, light, dialogue, combat and HUD.
 *
 * Controls (demo CONFIG pages + ch2 tutorial):
 *   2/4/6/8 or D-pad  move
 *   5 / FIRE          interact, pick up, stab (adjacent), shoot (ranged)
 *   1 or 3            toggle the light
 *   *                 pause
 */
class PlayScene extends Scene {
    int chapter;
    World world;
    Player player;
    Vector items;
    Vector enemies;
    Vector triggers;
    Vector sparks;              // impact effects {x, y, t}
    Dialogue dlg;
    Hud hud;

    int camX, camY;
    boolean inited = false;
    boolean flashOn = false;
    int batteryT = 0;
    int damageCd = 0;
    int deathT = -1;            // -1 alive, otherwise death animation timer

    boolean up, down, left, right;
    Trigger pending;
    boolean winning = false;
    int winT = 0;

    PlayScene(Game g, int chapter) {
        super(g);
        this.chapter = chapter;
    }

    void enter() {
        Assets.ensure();
        if (!inited) {
            inited = true;
            world = World.load(chapter);
            items = new Vector();
            enemies = new Vector();
            triggers = new Vector();
            sparks = new Vector();
            Script.populate(chapter, world, items, enemies, triggers);
            player = new Player();
            player.x = world.spawnX;
            player.y = world.spawnY;
            g.chapter = chapter;
            if (!g.hasFlashlight && chapter >= 3) {
                g.hasFlashlight = true;
            }
            dlg = new Dialogue();
            hud = new Hud();
            up = down = left = right = false;
        }
    }

    // ---------------------------------------------------------------- input
    private int dirOf(int key, int action) {
        if (action == Canvas.UP || key == Canvas.KEY_NUM2) {
            return 0;
        }
        if (action == Canvas.DOWN || key == Canvas.KEY_NUM8) {
            return 1;
        }
        if (action == Canvas.LEFT || key == Canvas.KEY_NUM4) {
            return 2;
        }
        if (action == Canvas.RIGHT || key == Canvas.KEY_NUM6) {
            return 3;
        }
        return -1;
    }

    void keyPressed(int key, int action) {
        if (winning) {
            if (winT > 90 && (action == Canvas.FIRE || key == Canvas.KEY_NUM5)) {
                g.setScene(new MenuScene(g));
            }
            return;
        }
        if (deathT >= 0) {
            return;
        }
        if (dlg != null && dlg.isActive()) {
            if (action == Canvas.FIRE || key == Canvas.KEY_NUM5) {
                if (dlg.advance()) {
                    finishTrigger();
                }
            }
            return;
        }
        if (key == Canvas.KEY_STAR || action == Canvas.GAME_A) {
            g.setScene(new PauseScene(g, this));
            return;
        }
        // 1 / 3 toggle the light (ch2 tutorial: "PRESS '1' OR '3'")
        if (key == Canvas.KEY_NUM1 || key == Canvas.KEY_NUM3
                || action == Canvas.GAME_B || action == Canvas.GAME_C) {
            if (g.hasFlashlight) {
                flashOn = !flashOn;
            }
            return;
        }
        if (action == Canvas.FIRE || key == Canvas.KEY_NUM5) {
            fire();
            return;
        }
        int d = dirOf(key, action);
        if (d == 0) {
            up = true;
        } else if (d == 1) {
            down = true;
        } else if (d == 2) {
            left = true;
        } else if (d == 3) {
            right = true;
        }
    }

    void keyReleased(int key) {
        int a = 0;
        try {
            a = g.getGameAction(key);
        } catch (Exception e) {
        }
        int d = dirOf(key, a);
        if (d == 0) {
            up = false;
        } else if (d == 1) {
            down = false;
        } else if (d == 2) {
            left = false;
        } else if (d == 3) {
            right = false;
        }
    }

    /** Facing offset for shots and stabs. */
    private int aimDx() {
        return player.aimX();
    }

    private int aimDy() {
        return player.aimY();
    }

    private void fire() {
        // 1. interact / pick up a nearby item
        for (int i = 0; i < items.size(); i++) {
            Item it = (Item) items.elementAt(i);
            if (it.taken) {
                continue;
            }
            int dx = it.x - player.x;
            int dy = it.y - player.y;
            if (dx * dx + dy * dy < 22 * 22) {
                take(it);
                return;
            }
        }
        // 2. stab a creature within arm's reach
        if (stabNearest(18, 1)) {
            return;
        }
        // 3. shoot, if armed
        if (g.hasGun && g.gunAmmo > 0) {
            g.gunAmmo--;
            player.shootT = 18;
            shoot();
            return;
        }
        // 4. nothing else: toggle the light
        if (g.hasFlashlight) {
            flashOn = !flashOn;
        }
    }

    private void shoot() {
        int ax = aimDx();
        int ay = aimDy();
        Enemy best = null;
        int bestD = 70 * 70;
        for (int i = 0; i < enemies.size(); i++) {
            Enemy e = (Enemy) enemies.elementAt(i);
            if (e.state == Enemy.ST_DYING) {
                continue;
            }
            int dx = e.x - player.x;
            int dy = (e.y - 8) - (player.y - 10);
            int along = dx * ax + dy * ay;          // projection on the aim ray
            if (along <= 0) {
                continue;
            }
            int perp = dx * ay - dy * ax;
            if (perp * perp > 12 * 12) {
                continue;
            }
            if (along * along < bestD) {
                bestD = along * along;
                best = e;
            }
        }
        if (best != null) {
            best.hit(2);
            addSpark(best.x, best.y - 10);
        }
        g.combatT = 180;
    }

    /** Stabs the nearest creature within reach; true when one was hit. */
    private boolean stabNearest(int reach, int dmg) {
        Enemy best = null;
        int bestD = reach * reach;
        for (int i = 0; i < enemies.size(); i++) {
            Enemy e = (Enemy) enemies.elementAt(i);
            if (e.state == Enemy.ST_DYING) {
                continue;
            }
            int dx = e.x - player.x;
            int dy = e.y - player.y;
            int d2 = dx * dx + dy * dy;
            if (d2 < bestD) {
                bestD = d2;
                best = e;
            }
        }
        if (best == null) {
            return false;
        }
        best.hit(dmg);
        addSpark(best.x + aimDx() * 6, best.y - 10 + aimDy() * 6);
        g.combatT = 180;
        return true;
    }

    private void addSpark(int x, int y) {
        sparks.addElement(new int[] { x, y, 0 });
    }

    private void take(Item it) {
        it.taken = true;
        switch (it.type) {
            case Item.FLASHLIGHT:
                g.hasFlashlight = true;
                flashOn = true;
                break;
            case Item.BATTERY:
                g.spareBatteries++;
                break;
            case Item.MEDKIT:
                g.health = Math.min(100, g.health + 40);
                break;
            case Item.KEY:
                g.hasKey = true;
                break;
            case Item.GUN:
                g.hasGun = true;
                g.gunAmmo += 4;
                break;
            case Item.AMMO:
                g.gunAmmo += 6;
                break;
            case Item.CROWBAR:
                g.hasCrowbar = true;
                break;
            case Item.PROD:
                g.hasGun = true;               // stand-in: counts as a weapon
                break;
        }
        Vector v = new Vector();
        v.addElement(new DLine(Assets.P_YOU, g.playerName, it.msg));
        dlg.start(v);
        pending = null;
    }

    private void finishTrigger() {
        Trigger t = pending;
        pending = null;
        if (t == null) {
            return;
        }
        switch (t.action) {
            case Trigger.ACT_DARK:
                world.dark = true;
                break;
            case Trigger.ACT_FLASHLIGHT:
                g.hasFlashlight = true;
                break;
            case Trigger.ACT_BATTERY:
                g.spareBatteries++;
                break;
            case Trigger.ACT_TORCH:
                g.hasFlashlight = true;
                flashOn = true;
                break;
            case Trigger.ACT_SUPPLY:
                g.hasGun = true;
                g.gunAmmo += 6;
                g.spareBatteries += 2;
                break;
            case Trigger.ACT_DAMAGE:
                hurt(25);
                break;
            case Trigger.ACT_END:
                if (chapter < 3) {
                    g.setScene(new LoadingScene(g, chapter + 1));
                } else {
                    g.setScene(new EndingScene(g));
                }
                break;
            case Trigger.ACT_DOOR:
                if (g.hasCrowbar) {
                    g.setScene(new EndingScene(g));
                }
                break;
        }
    }

    private void hurt(int dmg) {
        g.health -= dmg;
        g.combatT = 180;
        if (g.health <= 0) {
            g.health = 0;
            deathT = 0;
        }
    }

    // ---------------------------------------------------------------- update
    void update() {
        if (dlg != null && dlg.isActive()) {
            dlg.update();
            return;
        }
        if (winning) {
            winT++;
            return;
        }
        if (deathT >= 0) {
            deathT++;
            if (deathT > 60) {
                g.health = 100;
                g.battery = Math.max(g.battery, 60);
                g.setScene(new LoadingScene(g, chapter));
            }
            return;
        }
        int dx = 0, dy = 0;
        if (left) {
            dx -= player.speed;
        }
        if (right) {
            dx += player.speed;
        }
        if (up) {
            dy -= player.speed;
        }
        if (down) {
            dy += player.speed;
        }
        if (dx != 0 || dy != 0) {
            if (canMove(player.x + dx, player.y + dy)) {
                player.step(dx, dy);
            } else {
                if (canMove(player.x + dx, player.y)) {
                    player.step(dx, 0);
                } else if (canMove(player.x, player.y + dy)) {
                    player.step(0, dy);
                } else {
                    player.idle();
                }
            }
        } else {
            player.idle();
        }

        // battery drain: the cell in use empties, then a spare is loaded
        if (flashOn) {
            batteryT++;
            if (batteryT >= 9) {
                batteryT = 0;
                if (g.battery > 0) {
                    g.battery--;
                } else if (g.spareBatteries > 0) {
                    g.spareBatteries--;
                    g.battery = 100;
                } else {
                    flashOn = false;
                }
            }
        }

        // enemies
        int radius = world.lightRadius;
        boolean anyClose = false;
        for (int i = enemies.size() - 1; i >= 0; i--) {
            Enemy e = (Enemy) enemies.elementAt(i);
            e.update(world, player.x, player.y, flashOn, radius);
            if (e.state == Enemy.ST_DYING && e.dieT > 26) {
                enemies.removeElementAt(i);
                continue;
            }
            int ex = e.x - player.x;
            int ey = e.y - player.y;
            if (ex * ex + ey * ey < 90 * 90 && e.state != Enemy.ST_DYING) {
                anyClose = true;
            }
        }
        if (anyClose) {
            g.combatT = Math.max(g.combatT, 60);
        }

        // impact sparks
        for (int i = sparks.size() - 1; i >= 0; i--) {
            int[] s = (int[]) sparks.elementAt(i);
            s[2]++;
            if (s[2] > 8) {
                sparks.removeElementAt(i);
            }
        }

        // enemy contact
        if (damageCd > 0) {
            damageCd--;
        } else {
            for (int i = 0; i < enemies.size(); i++) {
                Enemy e = (Enemy) enemies.elementAt(i);
                if (e.state == Enemy.ST_DYING) {
                    continue;
                }
                int ex = e.x - player.x;
                int ey = e.y - player.y;
                if (ex * ex + ey * ey < 12 * 12) {
                    hurt(e.type == Enemy.WALKER ? 8 : 6);
                    damageCd = 24;
                    break;
                }
            }
        }

        // item pickup by walking over
        for (int i = 0; i < items.size(); i++) {
            Item it = (Item) items.elementAt(i);
            if (!it.taken) {
                int ix = it.x - player.x;
                int iy = it.y - player.y;
                if (ix * ix + iy * iy < 10 * 10) {
                    take(it);
                    break;
                }
            }
        }

        // triggers
        for (int i = 0; i < triggers.size(); i++) {
            Trigger t = (Trigger) triggers.elementAt(i);
            if (t.done) {
                // the crowbar door can be retried after walking away without one
                if (t.action == Trigger.ACT_DOOR && !t.contains(player.x, player.y)) {
                    t.done = false;
                }
                continue;
            }
            if (t.contains(player.x, player.y)) {
                t.done = true;
                pending = t;
                if (t.action == Trigger.ACT_DOOR && !g.hasCrowbar) {
                    dlg.start(Script.doorJamLines());
                } else {
                    dlg.start(t.lines);
                }
                break;
            }
        }

        // camera
        camX = player.x - Game.W / 2;
        camY = player.y - Game.H / 2;
        int maxX = world.widthTiles() * World.T - Game.W;
        int maxY = world.heightTiles() * World.T - Game.H;
        if (camX < 0) {
            camX = 0;
        }
        if (camY < 0) {
            camY = 0;
        }
        if (camX > maxX) {
            camX = maxX;
        }
        if (camY > maxY) {
            camY = maxY;
        }
    }

    private boolean canMove(int nx, int ny) {
        if (world.blocked(nx / World.T, (ny - 6) / World.T)) {
            return false;
        }
        if (world.blocked((nx - 5) / World.T, (ny - 12) / World.T)) {
            return false;
        }
        if (world.blocked((nx + 5) / World.T, (ny - 12) / World.T)) {
            return false;
        }
        return true;
    }

    // ---------------------------------------------------------------- paint
    void paint(Graphics gr) {
        paintWorldOnly(gr);
        if (dlg != null && dlg.isActive()) {
            dlg.paint(gr);
        }
        if (winning) {
            gr.setColor(0);
            if (winT > 90) {
                gr.fillRect(0, 0, Game.W, Game.H);
                Fnt.get(0xC03020).drawCenter(gr, "THE END", 88, 96);
                Fnt.get(0xD8C0A0).drawCenter(gr, "PRESS 5", 88, 120);
            }
        } else if (deathT > 6) {
            // the player falls: spread pose, then the green skull
            Image[] de = Assets.death;
            if (de != null && de[1] != null) {
                Image im = deathT < 30 ? de[1] : de[0];
                gr.drawImage(im, player.x - camX - (im.getWidth() >> 1),
                        player.y - camY - (im.getHeight() >> 1),
                        Graphics.TOP | Graphics.LEFT);
            }
        }
    }

    void paintWorldOnly(Graphics gr) {
        gr.setColor(0);
        gr.fillRect(0, 0, Game.W, Game.H);
        world.paint(gr, camX, camY);

        for (int i = 0; i < items.size(); i++) {
            Item it = (Item) items.elementAt(i);
            if (!it.taken) {
                it.paint(gr, camX, camY);
            }
        }
        for (int i = 0; i < enemies.size(); i++) {
            ((Enemy) enemies.elementAt(i)).paint(gr, camX, camY);
        }
        player.paint(gr, camX, camY, g);

        // impact sparks: tiny white bursts
        gr.setColor(0xFFFFFF);
        for (int i = 0; i < sparks.size(); i++) {
            int[] s = (int[]) sparks.elementAt(i);
            int t = s[2];
            if (t < 4) {
                gr.fillRect(s[0] - camX - 1, s[1] - camY - 1, 2, 2);
                gr.fillRect(s[0] - camX - 3 + t, s[1] - camY - 2, 1, 1);
                gr.fillRect(s[0] - camX + 2 - t, s[1] - camY + 1, 1, 1);
            }
        }

        // darkness closes in over everything that is not lit
        if (world.dark) {
            applyLight(gr);
        }

        hud.paint(gr, g, enemyNear(), chapter >= 2);
    }

    private boolean enemyNear() {
        for (int i = 0; i < enemies.size(); i++) {
            Enemy e = (Enemy) enemies.elementAt(i);
            if (e.state == Enemy.ST_DYING) {
                continue;
            }
            int ex = e.x - player.x;
            int ey = e.y - player.y;
            if (ex * ex + ey * ey < 70 * 70) {
                return true;
            }
        }
        return false;
    }

    /**
     * Darkness closes in around the player. The lit area is the same whether a
     * cut scene is playing or not: a tight, bright pool with the flashlight on,
     * a wider dimmer one without. The pool is centred on the player's body and
     * a wobble variant is picked from their position so the edge shifts as they
     * walk.
     */
    private void applyLight(Graphics gr) {
        Image[] set = flashOn ? Assets.lightG : Assets.lightGS;
        int v = ((player.x >> 5) ^ (player.y >> 5)) & 1;
        Image im = set[v];
        int R = im != null ? im.getWidth() / 2 : (flashOn ? 36 : 55);
        // flashlight beam: the pool points where the player is facing and
        // keeps that direction when he stops
        int ox = 0, oy = 0;
        int step = R / 2;
        if (player.aimX() != 0 && player.aimY() != 0) {
            step = (R * 2) / 5;
        }
        ox = player.aimX() * step;
        oy = player.aimY() * step;
        int lx = player.x - camX + ox;
        int ly = player.y - camY - 12 + oy;
        int x0 = lx - R;
        int y0 = ly - R;
        int x1 = lx + R;
        int y1 = ly + R;
        gr.setColor(0);
        if (y0 > 0) {
            gr.fillRect(0, 0, Game.W, y0);
        }
        if (y1 < Game.H) {
            gr.fillRect(0, y1, Game.W, Game.H - y1);
        }
        int cy0 = y0 < 0 ? 0 : y0;
        int cy1 = y1 > Game.H ? Game.H : y1;
        if (x0 > 0) {
            gr.fillRect(0, cy0, x0, cy1 - cy0);
        }
        if (x1 < Game.W) {
            gr.fillRect(x1, cy0, Game.W - x1, cy1 - cy0);
        }
        if (im != null) {
            gr.drawImage(im, x0, y0, Graphics.TOP | Graphics.LEFT);
        }
    }
}
