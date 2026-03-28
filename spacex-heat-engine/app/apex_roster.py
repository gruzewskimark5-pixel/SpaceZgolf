from datetime import datetime
from .apex_models import Player

ROSTER = {
    # -------------------------
    # WAVE 1 — STABILITY
    # -------------------------
    "asterisk_talley": Player(
        id="asterisk_talley", name="Asterisk Talley",
        cluster="Stability", base_heat=0.90, volatility=3.8, authority=8.0
    ),
    "gianna_clemente": Player(
        id="gianna_clemente", name="Gianna Clemente",
        cluster="Stability", base_heat=0.95, volatility=2.9, authority=9.8
    ),
    "megha_ganne": Player(
        id="megha_ganne", name="Megha Ganne",
        cluster="Stability", base_heat=1.05, volatility=5.6, authority=6.0
    ),
    "marissa_wenzler": Player(
        id="marissa_wenzler", name="Marissa Wenzler",
        cluster="Stability", base_heat=1.00, volatility=4.5, authority=7.0
    ),

    # -------------------------
    # WAVE 2 — CHAOS
    # -------------------------
    "alyssa_lamoureux": Player(
        id="alyssa_lamoureux", name="Alyssa Lamoureux",
        cluster="Chaos", base_heat=1.15, volatility=8.9, authority=4.5
    ),
    "alexis_miestowski": Player(
        id="alexis_miestowski", name="Alexis Miestowski",
        cluster="Chaos", base_heat=1.10, volatility=7.4, authority=5.0
    ),
    "playerx_phenom": Player(
        id="playerx_phenom", name="Player X (Phenom)",
        cluster="Chaos", base_heat=1.00, volatility=9.7, authority=3.0
    ),
    "playerx_shadow": Player(
        id="playerx_shadow", name="Player X (Shadow)",
        cluster="Chaos", base_heat=0.95, volatility=8.5, authority=3.5
    ),

    # -------------------------
    # WAVE 3 — NARRATIVE-COMMERCE
    # -------------------------
    "kai_trump": Player(
        id="kai_trump", name="Kai Trump",
        cluster="Narrative-Commerce", base_heat=1.40, volatility=4.9, authority=8.5
    ),
    "gabriella_degasperis": Player(
        id="gabriella_degasperis", name="Gabriella DeGasperis",
        cluster="Narrative-Commerce", base_heat=1.00, volatility=5.1, authority=4.0
    ),
    "sabrina_andolpho": Player(
        id="sabrina_andolpho", name="Sabrina Andolpho",
        cluster="Narrative-Commerce", base_heat=1.00, volatility=5.1, authority=4.0
    ),
    "hannah_greg": Player(
        id="hannah_greg", name="Hannah Greg",
        cluster="Narrative-Commerce", base_heat=1.05, volatility=4.2, authority=6.5
    ),
    "mia_baker": Player(
        id="mia_baker", name="Mia Baker",
        cluster="Narrative-Commerce", base_heat=1.00, volatility=3.9, authority=6.0
    ),

    # -------------------------
    # WAVE 4 — PRESTIGE
    # -------------------------
    "nelly_korda": Player(
        id="nelly_korda", name="Nelly Korda",
        cluster="Prestige", base_heat=1.20, volatility=3.1, authority=10.0
    ),
    "jessica_korda": Player(
        id="jessica_korda", name="Jessica Korda",
        cluster="Prestige", base_heat=1.10, volatility=3.0, authority=9.0
    ),
    "muni_he": Player(
        id="muni_he", name="Muni He",
        cluster="Prestige", base_heat=1.25, volatility=4.8, authority=7.5
    ),

    # -------------------------
    # CHAOS-LITE SUBCLUSTER
    # -------------------------
    "cailyn": Player(
        id="cailyn", name="Cailyn",
        cluster="Chaos", base_heat=1.10, volatility=8.1, authority=2.5
    ),
    "abbey": Player(
        id="abbey", name="Abbey",
        cluster="Chaos", base_heat=1.05, volatility=6.4, authority=3.0
    ),
    "phoebe": Player(
        id="phoebe", name="Phoebe",
        cluster="Chaos", base_heat=1.00, volatility=5.9, authority=2.8
    ),

    # -------------------------
    # NOISE-PLUS + ALGORITHM FAVORITES
    # -------------------------
    "karissa": Player(
        id="karissa", name="Karissa",
        cluster="Noise", base_heat=0.95, volatility=6.0, authority=2.0
    ),
    "claire_hogle": Player(
        id="claire_hogle", name="Claire Hogle",
        cluster="Noise", base_heat=1.05, volatility=6.8, authority=3.5
    ),
}
