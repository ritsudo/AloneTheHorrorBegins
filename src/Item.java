import javax.microedition.lcdui.Graphics;
import javax.microedition.lcdui.Image;

/** A collectable lying on the ground. */
class Item {
    static final int KEY = 0;
    static final int MEDKIT = 1;
    static final int BATTERY = 2;
    static final int FLASHLIGHT = 3;
    static final int PROD = 4;
    static final int NOTE = 5;
    static final int GUN = 6;
    static final int AMMO = 7;
    static final int CROWBAR = 8;

    int x, y;
    int type;
    boolean taken;
    String msg;

    Item(int x, int y, int type, String msg) {
        this.x = x;
        this.y = y;
        this.type = type;
        this.msg = msg;
    }

    Image image() {
        switch (type) {
            case KEY:
                return Assets.itemKey;
            case MEDKIT:
                return Assets.itemMedkit;
            case BATTERY:
                return Assets.hudCell;          // same art as the HUD cell
            case GUN:
                return Assets.itemGun;
            case AMMO:
                return Assets.itemAmmo;
            case CROWBAR:
                return Assets.itemCrowbar;
            case NOTE:
                return Assets.itemNote;
            case FLASHLIGHT:
            case PROD:
            default:
                return Assets.itemBatt;
        }
    }

    void paint(Graphics g, int camX, int camY) {
        Image im = image();
        if (im != null) {
            g.drawImage(im, x - camX - (im.getWidth() >> 1),
                    y - camY - (im.getHeight() >> 1),
                    Graphics.TOP | Graphics.LEFT);
        }
    }
}
