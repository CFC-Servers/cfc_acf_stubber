AddCSLuaFile()

DATA = {
    enabled = true,
    spread = 0.4,
    name = "13mm Heavy Machinegun",
    desc = "The lightest of the HMGs, the 13mm has a rapid fire rate but suffers from poor payload size.  Often used to strafe ground troops or annoy low-flying aircraft.",
    muzzleflash = "50cal_muzzleflash_noscale",
    rofmod = 3.3,
    sound = "weapons/ACF_Gun/mg_fire3.wav",
    soundDistance = " ",
    soundNormal = " ",
    longbarrel = {
        index = 2,
        submodel = 4,
        newpos = "muzzle2",
    },
    model = "models/machinegun/machinegun_20mm.mdl",
    gunclass = "HMG",
    caliber = 1.3,
    weight = 90,
    year = 1935,
    magsize = 35,
    magreload = 6,
    round = {
        maxlength = 22,
        propweight = 0.09,
    },
}