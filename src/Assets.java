import javax.microedition.lcdui.Image;

/**
 * Loads and caches every bitmap the game needs. Resource names are tried both
 * at the JAR root and inside "res/" so the project works with the WTK and with
 * hand built JARs.
 */
class Assets {
    static Image page, sign, logo, title;
    static Image heart, vein, veinRed, alert;
    static Image hudCell, hudCellRed, hudCellOff;
    static Image campfire;
    static Image player, howler, zombie;
    static Image[] death;
    static Image itemKey, itemMedkit, itemBatt, itemNote, itemGun, itemAmmo, itemCrowbar;
    static Image tileset;
    static Image font;
    static Image[] lightG, lightGS;
    static Image fontRed, fontCream;
    static Image fontBig;
    static Image[][] portraits;

    static final int P_YOU = 0;
    static final int P_JONATHAN = 1;
    static final int P_MAN = 2;

    private static boolean loaded = false;

    static Image load(String name) {
        Image im = null;
        try {
            im = Image.createImage("/" + name);
        } catch (Exception e) {
            try {
                im = Image.createImage("/res/" + name);
            } catch (Exception e2) {
                im = null;
            }
        }
        return im;
    }

    static void ensure() {
        if (loaded) {
            return;
        }
        page = load("page.png");
        sign = load("sign.png");
        logo = load("logo.png");
        title = load("title.png");
        heart = load("hud_heart.png");
        vein = load("hud_vein.png");
        veinRed = load("hud_vein_red.png");
        alert = load("hud_alert.png");
        hudCell = load("hud_cell.png");
        hudCellRed = load("hud_cell_red.png");
        hudCellOff = load("hud_cell_off.png");
        campfire = load("campfire.png");
        player = load("player_walk.png");
        howler = load("howler.png");
        zombie = load("zombie.png");
        death = new Image[] { load("death_skull.png"), load("death_spread.png") };
        itemKey = load("item_key.png");
        itemMedkit = load("item_medkit.png");
        itemBatt = load("item_batt.png");
        itemGun = load("item_gun.png");
        itemAmmo = load("item_ammo.png");
        itemCrowbar = load("item_crowbar.png");
        itemNote = page != null ? Image.createImage(page, 76, 92, 24, 24, 0) : null;
        tileset = load("tileset_grid.png");
        lightG = new Image[] { load("light_g0.png"), load("light_g1.png") };
        lightGS = new Image[] { load("light_gs0.png"), load("light_gs1.png") };
        font = load("font.png");
        fontRed = load("font_red.png");
        fontCream = load("font_cream.png");
        fontBig = load("font_big.png");

        portraits = new Image[3][];
        portraits[P_YOU] = new Image[] { load("p_you.png") };
        portraits[P_JONATHAN] = new Image[] { load("p_jonathan.png") };
        portraits[P_MAN] = new Image[] { load("p_man.png") };

        loaded = true;
    }
}
