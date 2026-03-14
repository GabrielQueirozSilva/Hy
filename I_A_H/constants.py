#Aqui fica as listas de possibilidades e constantes usadas no bot
LIMITE_DE_CONFIANCA_GERAL = 87
LIMITE_DE_CONFIANCA_PET = 88 

EQUIPAMENT_TITLES = ["helmet", "chestplate", "leggings", "boots", "sword", "bow", "pickaxe", "axe", "shovel", "fishing rod"]
CONSUMABLE_TITLE = ["power scroll", "potion", "voodo doll", "bottle of jerry", "grizzly salmon"]
CONSUMABLES_KEYWORDS = ["consumable", "consumables", "consumed", "consume", "click to read!"]
TIERS = ["legendary", "epic", "rare", "common", "uncommon", "mythic", "special", "divine", "very special"]
PET_TYPES = ["elephant", "blue whale", "enderman", "silverfish","Armadillo","endermite","glacite golem", "scatcha", "bal", "bat", "mole",
             "mithril golem", "rat", "rabbit", "tiger", "grandma wolf", "snail", "wither skeleton", "goblin", "Ankylosaurus", "black cat",
             "reindeer", "rock", "guardian", "golden dragon", "armadillo", "monkey", "sheep", "mushroom cow", "blaze", "eeire",
             "ender dragon", "ghoul", "golem", "griffin", "horse", "hound", "jerry", "kuudra", "magma cube", "mammoth", "phoenix", "pigman",
             "rift ferret", "skeleton horse", "skeleton", "snowman", "spider", "squid", "tarantula", "spirit", "turtle", "t-rex", "zombie",
             "wolf", "bee", "chicken", "hedgehog", "pig", "slug", "girafe", "lion", "ocelot", "ammonite", "baby yeti", "dolphin", "flying fish",
             "megalodon", "penguin", "spinosarus", "hermit crab", "jellyfish", "parrot", "owl", "bingo", "montezuma", "wisp"]
PRICE_KEYWORDS = ["buy it now:", "it now:", "now:", "coins"]
COSMETIC_KEYWORDS = ["skin", "pet skins", "change the look", "skin can be active", "this skin"]
DUNGEON_KEYWORDS = ["gear score:", "score:", "gear"]
ACCESSORY_KEYWORDS = ["accessory"]
PET_ITENS_KEYWORDS = ["pet item", "pet food", "right-click to feed",]
SELLER_KEYWORDS = ["seller:","seller=","sellen-","sellen"]

# 1. Correções GLOBAIS (Rodam em tudo)
GLOBAL_REPLACEMENTS = {
    "accessort": "accessory", "accessont": "accessory",
    "acessory": "accessory",
    # "Refongedi": "reforged!", "berefongedi": "be reforged!", "berefongedi": "be reforged!", "refongedi": "reforged!", "bereforged": "be reforged!",
    "Defenset": "Defense", "DefenSe": "Defense", "IDefense": "Defense", "defense_": "Defense",
    "Endsin": "Ends in", "endsin": "Ends in", "iends": "ends",
    "Hining": "Mining",
    "iten": "item", "itam": "item", "iteh": "item",
    "mtthic": "mythic", "NTTHIC": "mythic", "mtthic": "mythic", "LEgendart": "legendary", "rar": "rare", "legenart": "legendary",
    "Oear": "Gear", "Oean": "Gear",
    "Orants": "Grants",
    " ortune": "fortune",
    "Pouen": "Power", "Powen": "Power", "Pouer": "Power",
    "Scone:": "Score",
    "Defenseand": "Defense and",
    "(nining": "Mining", "Nining": "Mining", "Miming": "Mining", "INining": "Mining", "IMining": "Mining",
    ";": ":",
}

NAMES_REPLACEMENTS = {
    "Leggingsof": "leggings of",
    "BootsOf": "boots of", "dootsof": "boots of", "dootsf": "boots of",
    "Meat": "Heat",
    "HegenonyAntiface": "Hegemony Artifact", "Antifact": "Artifact",
    "Helnet": "Helmet", "HELHET": "Helmet", "helret": "Helmet",
    "Dox": "Box",
    "jyrre": "jerry",
    "Conpacton": "compactor",
    "@Ruudras Heant": "Rudras Heart",
    "prisn": "prism",
    "Scrol": "Scroll",
    "artifactof": "artifact of", 
}


SELLER_REPLACEMENTS = {
    "sellen-": "seller:", "seller-": "seller:", "seller=": "seller:", "sellen": "seller:", 
    "seller ": "seller:", "sellen:": "seller:", "jeller:": "seller:", "sellern:": "seller:",
    
    "[mvp ]": "[MPV]", 
    "[vip+ ": "[VIP+]",
}

# 2. Correções Específicas de PREÇO (Contexto 'PRICE')
PRICE_REPLACEMENTS = {
    "bui": "Buy", "by": "Buy", "ibuy": "buy",
    "nou:": "now:", "noew:": "now:", "nol:": "now:", "ol:": "now:",
    "coims": "coins", "coms": "coins", "corns": "coins",
    "Buyit": "Buy it",
    "IBuy": "Buy",
}
