AddCSLuaFile()

DATA = {
    enabled = true,
    spread = 0.4,
    name = "20mm Heavy Machinegun",
    desc = "The 20mm has a rapid fire rate but suffers from poor payload size.  Often used to strafe ground troops or annoy low-flying aircraft.",
    muzzleflash = "50cal_muzzleflash_noscale",
    rofmod = 1.9,
    sound = "weapons/ACF_Gun/mg_fire3.wav",
    soundDistance = " ",
    soundNormal = " ",
    longbarrel = {
        index = 2,
        submodel = 4,
        newpos = "muzzle2",
    },
    model = "models/machinegun/machinegun_20mm_compact.mdl",
    gunclass = "HMG",
    caliber = 2.0,
    weight = 160,
    year = 1935,
    magsize = 30,
    magreload = 6,
    round = {
        maxlength = 30,
        propweight = 0.12,
    },
}