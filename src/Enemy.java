import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;
import javax.microedition.lcdui.game.Sprite;

/**
 * A creature. HOWLERS are ghosts: they fly through walls, ignore weapons and
 * flee from the flashlight. WALKERS are the pale dead: they collide with the
 * world and can be shot or stabbed.
 */
class Enemy {
    static final int HOWLER = 0;
    static final int WALKER = 1;

    static final int FW_Z = 14;      // zombie_full.png cell
    static final int FH_Z = 24;
    static final int FW_H = 20;      // howler_full.png cell
    static final int FH_H = 24;

    static final int Z_RIGHT = 0;
    static final int Z_LEFT = 1;
    static final int Z_DOWN = 2;
    static final int Z_UP = 3;

    static final int H_LEFT = 0;     // 3-frame walk (0..2)
    static final int H_RIGHT = 3;    // 3-frame walk (3..5)
    static final int H_DOWN = 6;     // single frame
    static final int H_UP = 7;       // single frame
    static final int H_HOWL0 = 8;
    static final int H_HOWL1 = 9;

    static final int ST_WALK = 0;
    static final int ST_RETREAT = 1;
    static final int ST_DYING = 2;

    static final int DEATH_FRAME = 32;
    static final int DEATH_TICKS = 4;

    int x, y;
    int type;
    int hp;
    int state = ST_WALK;
    int dir = Game.DIR_DOWN;
    int frame = 0;
    int animT = 0;
    int wanderT = 0;
    int wx = 0, wy = 0;
    int dieT = 0;
    int hurtT = 0;
    int retreatDist = 0;
    int howlT = 0;
    long lastHowl = 0;
    long dirUntil = 0;
    int speed = 1;

    Enemy(int x, int y, int type) {
        this.x = x;
        this.y = y;
        this.type = type;
        hp = type == HOWLER ? 0 : 3;
        speed = type == HOWLER ? 2 : 1;
    }

    boolean lit(int px, int py, boolean flash, int radius,
            int ax, int ay) {
        if (!flash) {
            return false;
        }
        // the beam pool sits ahead of the player, in the facing direction
        int step = radius / 3;
        int lx = px + ax * step;
        int ly = py + ay * step;
        int dx = x - lx;
        int dy = (y - 6) - (ly - 10);
        return dx * dx + dy * dy < radius * radius;
    }

    /** True when the creature is inside the player's ~90 degree front cone. */
    private boolean inFront(int px, int py, int ax, int ay) {
        if (ax == 0 && ay == 0) {
            return true;
        }
        int dx = x - px;
        int dy = y - py;
        return dx * ax + dy * ay >= 0;
    }

    private void die() {
        if (state == ST_DYING) {
            return;
        }
        state = ST_DYING;
        dieT = 0;
        AudioManager.playOnce("enemy_death.mid");
    }

    void hit(int dmg) {
        if (state == ST_DYING || type == HOWLER) {
            return;                 // ghosts cannot be cut or shot
        }
        hp -= dmg;
        hurtT = 6;
        if (hp <= 0) {
            die();
        }
    }

    void update(World world, int px, int py, boolean flash, int radius,
            int ax, int ay) {
        if (state == ST_DYING) {
            dieT++;
            return;
        }
        if (hurtT > 0) {
            hurtT--;
        }
        int dx = px - x;
        int dy = py - y;
        int d2 = dx * dx + dy * dy;

        if (type == HOWLER) {
            // facing a howler sends it fleeing, but only when it is close:
            // five tiles is the player's reach with the beam
            if (state != ST_RETREAT && d2 <= (World.T * 5) * (World.T * 5)
                    && inFront(px, py, ax, ay)) {
                state = ST_RETREAT;
                retreatDist = 0;
                dirUntil = 0;       // pick the retreat direction now
            }
            if (state == ST_RETREAT) {
                int adx = x - px;
                int ady = y - py;
                int mvx, mvy;
                if (Math.abs(adx) >= Math.abs(ady)) {
                    mvx = adx >= 0 ? speed : -speed;
                    mvy = 0;
                } else {
                    mvx = 0;
                    mvy = ady >= 0 ? speed : -speed;
                }
                x += mvx;           // ghosts ignore collision
                y += mvy;
                retreatDist += speed;
                setDir(mvx, mvy, px);
                animate(3, 7);
                if (retreatDist >= 48) {      // about three tiles
                    die();
                }
                return;
            }
            // a ghost behind or beside the player only announces itself
            if (!inFront(px, py, ax, ay) && d2 < 120 * 120) {
                long now = System.currentTimeMillis();
                if (now - lastHowl >= 2000) {
                    lastHowl = now;
                    howlT = 8;
                    AudioManager.playOnce((now & 1) == 0
                            ? "howler1.mid" : "howler2.mid");
                }
            }
            if (howlT > 0) {
                howlT--;
            }
        }

        int mvx = 0, mvy = 0;
        if (d2 < 90 * 90) {
            if (d2 > 14 * 14) {                 // close in, keep some slack
                if (dx * dx > dy * dy) {
                    mvx = dx > 0 ? speed : -speed;
                } else {
                    mvy = dy > 0 ? speed : -speed;
                }
            }
        } else {
            wanderT--;
            if (wanderT <= 0) {
                wanderT = 30 + (int) (System.currentTimeMillis() % 45);
                long t = System.currentTimeMillis();
                wx = (int) (t % 3) - 1;
                wy = (int) ((t >> 3) % 3) - 1;
                if (wx == 0 && wy == 0) {
                    wx = 1;
                }
            }
            mvx = wx;
            mvy = wy;
        }
        if (mvx != 0 || mvy != 0) {
            int nx = x + mvx;
            int ny = y + mvy;
            if (type == HOWLER) {
                x = nx;             // ghosts fly over all terrain
                y = ny;
            } else if (!world.blocked(nx / World.T, (ny - 6) / World.T)) {
                x = nx;
                y = ny;
            } else if (!world.blocked(nx / World.T, (y - 6) / World.T)) {
                x = nx;
            } else if (!world.blocked(x / World.T, (ny - 6) / World.T)) {
                y = ny;
            } else {
                wanderT = 0;
            }
            setDir(mvx, mvy, px);
            animate(type == HOWLER ? 3 : 4, type == HOWLER ? 7 : 6);
        }
    }

    /**
     * Left/right animation wins whenever there is sideways motion. Up/down
     * is used only when the enemy moves vertically on a straight line with the
     * player (within one tile); otherwise the side sequence is used.
     */
    private void setDir(int mvx, int mvy, int px) {
        if (mvx == 0 && mvy == 0) {
            return;
        }
        long now = System.currentTimeMillis();
        if (now < dirUntil) {
            return;                 // keep the chosen pose for 2.5 seconds
        }
        if (mvx != 0) {
            dir = mvx < 0 ? Game.DIR_LEFT : Game.DIR_RIGHT;
        } else if (Math.abs(x - px) <= World.T) {
            dir = mvy < 0 ? Game.DIR_UP : Game.DIR_DOWN;
        } else {
            dir = x < px ? Game.DIR_RIGHT : Game.DIR_LEFT;
        }
        dirUntil = now + 2500;
    }

    private void animate(int frames, int period) {
        animT++;
        if (animT > period) {
            animT = 0;
            frame = (frame + 1) % frames;
        }
    }

    void paint(Graphics g, int camX, int camY) {
        if (state == ST_DYING) {
            Image sheet = Assets.deathFull;
            if (sheet == null) {
                return;
            }
            int f = dieT / DEATH_TICKS;
            if (f > 7) {
                f = 7;
            }
            g.drawRegion(sheet, f * DEATH_FRAME, 0, DEATH_FRAME, DEATH_FRAME,
                    Sprite.TRANS_NONE, x - camX - DEATH_FRAME / 2,
                    y - camY - DEATH_FRAME + 8, Graphics.TOP | Graphics.LEFT);
            return;
        }
        if (type == WALKER) {
            Image sheet = Assets.zombieFull;
            if (sheet == null) {
                return;
            }
            int row;
            if (dir == Game.DIR_RIGHT) {
                row = Z_RIGHT;
            } else if (dir == Game.DIR_LEFT) {
                row = Z_LEFT;
            } else if (dir == Game.DIR_UP) {
                row = Z_UP;
            } else {
                row = Z_DOWN;
            }
            g.drawRegion(sheet, (frame & 3) * FW_Z, row * FH_Z,
                    FW_Z, FH_Z, Sprite.TRANS_NONE,
                    x - camX - FW_Z / 2, y - camY - FH_Z + 4,
                    Graphics.TOP | Graphics.LEFT);
        } else {
            Image sheet = Assets.howlerFull;
            if (sheet == null) {
                return;
            }
            int cell;
            if (howlT > 0 && state != ST_RETREAT) {
                cell = howlT > 4 ? H_HOWL0 : H_HOWL1;
            } else if (dir == Game.DIR_LEFT) {
                cell = H_LEFT + (frame % 3);
            } else if (dir == Game.DIR_RIGHT) {
                cell = H_RIGHT + (frame % 3);
            } else if (dir == Game.DIR_UP) {
                cell = H_UP;
            } else {
                cell = H_DOWN;
            }
            g.drawRegion(sheet, cell * FW_H, 0, FW_H, FH_H, Sprite.TRANS_NONE,
                    x - camX - FW_H / 2, y - camY - FH_H + 6,
                    Graphics.TOP | Graphics.LEFT);
        }
    }
}
