import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.game.Sprite;

/**
 * The player character. The sheet (res/player.png) holds 4 directions x 3
 * real walk poses cut from the demo capture (20x28 cells, order down, up,
 * left, right). Pose 1 is the passing stance and doubles as the idle pose.
 */
class Player {
    static final int FW = 20;
    static final int FH = 28;
    static final int[] CYCLE = {0, 1, 2, 1};

    int x, y;
    int dir = Game.DIR_DOWN;
    int frame = 0;
    int animT = 0;
    int speed = 2;
    boolean moving = false;
    int shootT = 0;          // muzzle flash / recoil timer

    void step(int dx, int dy) {
        if (dx != 0) {
            dir = dx < 0 ? Game.DIR_LEFT : Game.DIR_RIGHT;
        } else if (dy != 0) {
            dir = dy < 0 ? Game.DIR_UP : Game.DIR_DOWN;
        }
        x += dx;
        y += dy;
        moving = true;
        animT++;
        if (animT > 6) {
            animT = 0;
            frame = CYCLE[(animSeq = (animSeq + 1) & 3)];
        }
        if (shootT > 0) {
            shootT--;
        }
    }

    int animSeq = 0;

    void idle() {
        moving = false;
        frame = 1;
        animT = 0;
        animSeq = 0;
        if (shootT > 0) {
            shootT--;
        }
    }

    /** The sheet cell for the current direction and pose. */
    int cell() {
        return dir * 3 + frame;
    }

    void paint(Graphics g, int camX, int camY, Game game) {
        int cx = cell() * FW;
        int px = x - camX - FW / 2;
        int py = y - camY - FH + 2;
        g.drawRegion(Assets.player, cx, 0, FW, FH, Sprite.TRANS_NONE,
                px, py, Graphics.TOP | Graphics.LEFT);
        // the red gun held two-handed while armed (demo 3063..3108)
        if (game != null && game.hasGun && Assets.itemGun != null) {
            int gx, gy;
            int tr = Sprite.TRANS_NONE;
            switch (dir) {
                case Game.DIR_LEFT:
                    gx = px + 1;
                    gy = py + 19;
                    break;
                case Game.DIR_RIGHT:
                    gx = px + FW - 10;
                    gy = py + 19;
                    tr = Sprite.TRANS_MIRROR;
                    break;
                case Game.DIR_UP:
                    gx = px + (FW >> 1) - 2;
                    gy = py + 16;
                    break;
                default:
                    gx = px + (FW >> 1) - 2;
                    gy = py + 18;
                    break;
            }
            g.drawImage(Assets.itemGun, gx, gy, Graphics.TOP | Graphics.LEFT);
            if (shootT > 10) {
                // muzzle flash: a small burst past the barrel
                g.setColor(0xFFF0A0);
                int fx = dir == Game.DIR_LEFT ? gx - 4
                        : dir == Game.DIR_RIGHT ? gx + 8 : gx + 4;
                int fy = gy + 2;
                g.fillRect(fx, fy, 3, 2);
                g.fillRect(fx + (dir == Game.DIR_LEFT ? -2 : 3), fy + 1, 2, 1);
            }
        }
    }
}
