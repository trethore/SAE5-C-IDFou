unique_ordinal_values: set[str] = {
    "age_range",
    "frequency",
    "feeling_pref",
    "is_live_pref",
}

unique_non_ordinal_values: set[str] = {
    "gender",
    "position",
}

multi_values: set[str] = {
    "energy_pref",
    "context",
    "how",
    "platform",
    "utility",
}


pref_to_vec_map: dict[str, dict[str, None | dict[str, float]]] = {
    "age_range": {
        "age_range": {
            "entre 13 et 18 ans": 0.0,
            "entre 19 et 24 ans": 1.0,
            "entre 25 et 34 ans": 2.0,
            "entre 35 et 44 ans": 3.0,
            "entre 45 et 54 ans": 4.0,
            "entre 55 et 64 ans": 5.0,
            "65 ans et +": 6.0,
        }
    },
    "gender_men": {
        "gender": {
            "homme": 1.0,
        }
    },
    "gender_women": {
        "gender": {
            "femme": 1.0,
        }
    },
    "gender_other": {
        "gender": {
            "autre": 1.0,
        }
    },
    "gender_unknown": {
        "gender": {
            "préfère ne pas dire": 1.0,
        }
    },
    "position_administrative": {
        "position": {
            "redacteur administratif": 1.0,
            "administratif telecom": 1.0,
        }
    },
    "position_agriculture": {"position": {"agriculture": 1.0}},
    "position_animation": {
        "position": {
            "animation": 1.0,
        }
    },
    "position_army": {
        "position": {
            "armée": 1.0,
        }
    },
    "position_arts_medias": {
        "position": {
            "arts & médias": 1.0,
        }
    },
    "position_childhood": {
        "position": {
            "petite enfance": 1.0,
            "enfance": 1.0,
        }
    },
    "position_civil_servant": {
        "position": {
            "fonctionnaire": 1.0,
        }
    },
    "position_commerce_services": {
        "position": {
            "commerce & services": 1.0,
        }
    },
    "position_communication": {
        "position": {
            "communication": 1.0,
        }
    },
    "position_construction_industry": {
        "position": {
            "construction & industrie": 1.0,
        }
    },
    "position_culture": {
        "position": {
            "culture": 1.0,
        }
    },
    "position_education": {
        "position": {
            "éducation": 1.0,
        }
    },
    "position_environment": {
        "position": {
            "environnement": 1.0,
        }
    },
    "position_government": {
        "position": {
            "etat": 1.0,
            "fonction territoriale": 1.0,
        }
    },
    "position_health": {
        "position": {
            "santé": 1.0,
        }
    },
    "position_inactive": {
        "position": {
            "en invalidité": 1.0,
            "retraite": 1.0,
            "ne peux plus travailler": 1.0,
        }
    },
    "position_magnetism": {
        "position": {
            "magnétiseuse": 1.0,
        }
    },
    "position_maternity": {
        "position": {
            "assistante maternelle": 1.0,
        }
    },
    "position_sciences": {
        "position": {
            "sciences humaines": 1.0,
        }
    },
    "position_service": {
        "position": {
            "service": 1.0,
        }
    },
    "position_student": {
        "position": {
            "étudiant": 1.0,
            "étudiante": 1.0,
            "etudiant": 1.0,
            "etudiante": 1.0,
            "formation": 1.0,
            "etudiant en sciences": 1.0,
        }
    },
    "position_social": {
        "position": {
            "sociale": 1.0,
        }
    },
    "position_technology": {
        "position": {
            "technologie & informatique": 1.0,
        }
    },
    "position_transport": {
        "position": {
            "transport": 1.0,
            "taxis": 1.0,
        }
    },
    "position_unknown": {
        "position": {
            "préfère ne pas dire": 1.0,
        }
    },
    "frequency": {
        "frequency": {
            "+ d'une fois par semaine": 0.0,
            "+ d'une fois par jour": 1.0,
            "+ d'une fois par mois": 2.0,
        },
    },
    "when_listening": {
        "when_listening": None,
    },
    "duration_pref": {
        "duration_pref": None,
    },
    "energy_pref_background_voice": {
        "energy_pref": {
            "avec une voix mais en fond": 1.0,
        }
    },
    "energy_pref_instrumental": {
        "energy_pref": {
            "uniquement instrumentaux": 1.0,
        }
    },
    "energy_pref_with_lyrics": {
        "energy_pref": {
            "avec des paroles": 1.0,
        }
    },
    "tempo_pref": {
        "tempo_pref": None,
    },
    "feeling_pref": {
        "feeling_pref": {
            "positives": 0.0,
            "tristes": 1.0,
        }
    },
    "is_live_pref": {
        "is_live_pref": {
            "non": 0.0,
            "oui": 1.0,
        }
    },
    "quality_pref": {
        "quality_pref": None,
    },
    "curiosity_pref": {
        "curiosity_pref": None,
    },
    "context_alone": {
        "context": {
            "seul(e)": 1.0,
        }
    },
    "context_family": {
        "context": {
            "en famille": 1.0,
        }
    },
    "context_friends": {
        "context": {
            "entre amis": 1.0,
        }
    },
    "context_party": {
        "context": {
            "en fête": 1.0,
        }
    },
    "context_other": {
        "context": {
            "autre": 1.0,
        }
    },
    "how_cassette": {
        "how": {
            "cassettes": 1.0,
        }
    },
    "how_cd": {
        "how": {
            "cd": 1.0,
            "mp3 de musique chargée à partir de cd": 1.0,
        }
    },
    "how_concert": {"how": {"concert": 1.0}},
    "how_downloads": {
        "how": {
            "téléchargements": 1.0,
        }
    },
    "how_festival": {
        "how": {
            "festival": 1.0,
        }
    },
    "how_live": {
        "how": {
            "en live": 1.0,
        }
    },
    "how_radio": {
        "how": {
            "radio": 1.0,
            "en roulant en voiture (radio)": 1.0,
            "radio ordinateur": 1.0,
            "en voiture": 1.0,
            "autoradios": 1.0,
        }
    },
    "how_streaming": {
        "how": {
            "streaming": 1.0,
            "you tube": 1.0,
            "télé .... sur mon ordi": 1.0,
            "youtube": 1.0,
        }
    },
    "how_vinyl": {"how": {"vinyle": 1.0}},
    "platform_amazon_music": {
        "platform": {
            "amazonmusic": 1.0,
            "amazone music": 1.0,
        }
    },
    "platform_apple_music": {
        "platform": {
            "apple music": 1.0,
        }
    },
    "platform_deezer": {
        "platform": {
            "deezer": 1.0,
        }
    },
    "platform_shazam": {
        "platform": {
            "shazam": 1.0,
        }
    },
    "platform_spotify": {
        "platform": {
            "spotify": 1.0,
        }
    },
    "platform_soundcloud": {
        "platform": {
            "soundcloud": 1.0,
        }
    },
    "platform_youtube": {
        "platform": {
            "youtube": 1.0,
        }
    },
    "platform_youtube_alt": {
        "platform": {
            "youtube revanced": 1.0,
        }
    },
    "platform_youtube_music": {
        "platform": {
            "youtube music": 1.0,
        }
    },
    "utility_background": {
        "utility": {
            "fond musical  pendant  le travail ou au volant  de ma voiture": 1.0,
            "mp3 utilisé pendant la natation en piscine.": 1.0,
        }
    },
    "utility_concentrate": {
        "utility": {
            "se concentrer": 1.0,
        }
    },
    "utility_dance": {
        "utility": {
            "danser": 1.0,
        }
    },
    "utility_escape": {
        "utility": {
            "s'échapper": 1.0,
        }
    },
    "utility_kill_time": {
        "utility": {
            "passer le temps": 1.0,
        }
    },
    "utility_party": {
        "utility": {
            "faire la fête": 1.0,
        }
    },
    "utility_retreat_into_oneself": {
        "utility": {
            "se mettre dans sa bulle": 1.0,
        }
    },
}
