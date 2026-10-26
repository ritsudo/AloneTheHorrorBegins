import java.util.Vector;

/** An area that fires a conversation (and possibly an action) once entered. */
class Trigger {
    static final int ACT_NONE = 0;
    static final int ACT_DARK = 1;
    static final int ACT_FLASHLIGHT = 2;
    static final int ACT_BATTERY = 3;
    static final int ACT_END = 4;
    static final int ACT_TORCH = 5;
    static final int ACT_DAMAGE = 6;
    static final int ACT_SUPPLY = 7;     // Jonathan's supplies: gun + cells
    static final int ACT_DOOR = 8;       // chapter 3 red doors (needs crowbar)

    int x1, y1, x2, y2;
    boolean done = false;
    Vector lines;
    int action = ACT_NONE;

    Trigger(int x1, int y1, int x2, int y2, Vector lines, int action) {
        this.x1 = x1;
        this.y1 = y1;
        this.x2 = x2;
        this.y2 = y2;
        this.lines = lines;
        this.action = action;
    }

    boolean contains(int x, int y) {
        return x >= x1 && x <= x2 && y >= y1 && y <= y2;
    }
}
