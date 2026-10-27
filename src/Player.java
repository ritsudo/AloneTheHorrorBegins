import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.game.Sprite;

/**
 * The player character. The sheet (res/player_walk.png) is an 8-direction
 * walk grid: 6 frames of 14x25 px per row, in the order up, left-up, left,
 * left-down, down, right-up, right, right-down.
 */
class Player {
    static final int FW = 14;
    static final int FH = 25;
    static final int FRAMES = 6;

    static final int UP = 0;
    static final int LEFT_UP = 1;
    static final int LEFT = 2;
    static final int LEFT_DOWN = 3;
    static final int DOWN = 4;
    static final int RIGHT_UP = 5;
    static final int RIGHT = 6;
    static final int RIGHT_DOWN = 7;

    int x, y;
    int dir = DOWN;
    int frame = 0;
    int animT = 0;
    int speed = 2;
    boolean moving = false;
    int shootT = 0;          // muzzle flash / recoil timer

    // clockwise / counter-clockwise next facing (indexed by dir)
    private static final int[] CW = {
        RIGHT_UP, UP, LEFT_UP, LEFT, LEFT_DOWN, RIGHT, RIGHT_DOWN, DOWN
    };
    private static final int[] CCW = {
        LEFT_UP, LEFT, LEFT_DOWN, DOWN, RIGHT_DOWN, UP, RIGHT_UP, RIGHT
    };

    /** Tank steering: rotate the facing one 45-degree step. */
    void turn(int delta) {
        dir = delta > 0 ? CW[dir] : CCW[dir];
    }

    void step(int dx, int dy) {
        x += dx;
        y += dy;
        moving = true;
        animT++;
        if (animT > 3) {
            animT = 0;
            frame = (frame + 1) % FRAMES;
        }
        if (shootT > 0) {
            shootT--;
        }
    }

    void idle() {
        moving = false;
        frame = 0;
        animT = 0;
        if (shootT > 0) {
            shootT--;
        }
    }

    int aimX() {
        if (dir == LEFT || dir == LEFT_UP || dir == LEFT_DOWN) {
            return -1;
        }
        if (dir == RIGHT || dir == RIGHT_UP || dir == RIGHT_DOWN) {
            return 1;
        }
        return 0;
    }

    int aimY() {
        if (dir == UP || dir == LEFT_UP || dir == RIGHT_UP) {
            return -1;
        }
        if (dir == DOWN || dir == LEFT_DOWN || dir == RIGHT_DOWN) {
            return 1;
        }
        return 0;
    }

    /** The sheet cell for the current direction and animation frame. */
    int cell() {
        return dir * FRAMES + frame;
    }

    void paint(Graphics g, int camX, int camY, Game game) {
        int cx = frame * FW;
        int cy = dir * FH;
        int px = x - camX - FW / 2;
        int py = y - camY - FH + 2;
        g.drawRegion(Assets.player, cx, cy, FW, FH, Sprite.TRANS_NONE,
                px, py, Graphics.TOP | Graphics.LEFT);
        // the red gun held while armed (demo 3063..3108)
        if (game != null && game.hasGun && Assets.itemGun != null) {
            int ax = aimX();
            int ay = aimY();
            int gx = px + (FW >> 1) - 4 + ax * 4;
            int gy = py + FH - 8 + ay * 4;
            int tr = ax > 0 ? Sprite.TRANS_MIRROR : Sprite.TRANS_NONE;
            g.drawRegion(Assets.itemGun, 0, 0,
                    Assets.itemGun.getWidth(), Assets.itemGun.getHeight(),
                    tr, gx, gy, Graphics.TOP | Graphics.LEFT);
            if (shootT > 10) {
                // muzzle flash: a small burst past the barrel
                g.setColor(0xFFF0A0);
                int fx = gx + (ax < 0 ? -4 : ax > 0 ? 8 : 4);
                int fy = gy + (ay < 0 ? -2 : ay > 0 ? 4 : 2);
                g.fillRect(fx, fy, 3, 2);
                g.fillRect(fx + (ax < 0 ? -2 : 3), fy + 1, 2, 1);
            }
        }
    }
}
