eventironmental_data = [
  {
    "event_name": "long_sleep",
    "source": "unknown",
    "description": "A single long sleep episode per participant per day, starting at night (20:00-24:00), lasting 6-9 hours.",
    "characteristics": {
      "required": [
        "id",
        "type",
        "starttime",
        "endtime",
        "duration"
      ],
      "optional": []
    },
    "temporal_constraints": {
      "per_event_duration": {
        "min": 6,
        "max": 9,
        "unit": "hours"
      },
      "total_event_duration": {
        "scale": "day",
        "min": 6,
        "max": 9,
        "unit": "hours"
      },
      "total_event_episodes": {
        "scale": "day",
        "min": 1,
        "max": 1,
        "unit": "number"
      },
      "temporal_patterns": [
        {
          "mode": "seasonality",
          "details": {
            "scale": "night",
            "direction": "increasing",
            "amount": 100,
            "unit": "percentage",
            "within": [
              "night"
            ]
          }
        }
      ]
    }
  },
  {
    "event_name": "working",
    "source": "unknown",
    "description": "Two working episodes per participant per weekday, each 3-5 hours, total 6-9 hours, only in morning and afternoon, none on weekends.",
    "characteristics": {
      "required": [
        "id",
        "type",
        "starttime",
        "endtime",
        "duration"
      ],
      "optional": []
    },
    "temporal_constraints": {
      "per_event_duration": {
        "min": 3,
        "max": 5,
        "unit": "hours"
      },
      "total_event_duration": {
        "scale": "day",
        "min": 6,
        "max": 9,
        "unit": "hours"
      },
      "total_event_episodes": {
        "scale": "day",
        "min": 2,
        "max": 2,
        "unit": "number"
      },
      "temporal_patterns": [
        {
          "mode": "seasonality",
          "details": {
            "scale": "weekday",
            "direction": "increasing",
            "amount": 100,
            "unit": "percentage",
            "within": [
              "Monday",
              "Tuesday",
              "Wednesday",
              "Thursday",
              "Friday"
            ]
          }
        },
        {
          "mode": "seasonality",
          "details": {
            "scale": "day_part",
            "direction": "increasing",
            "amount": 100,
            "unit": "percentage",
            "within": [
              "morning",
              "afternoon"
            ]
          }
        }
      ]
    }
  },
  {
    "event_name": "walking",
    "source": "unknown",
    "description": "Walking episodes per participant per day, 2-8 times, each 10-60 minutes, total 1-4 hours/day. Morning: +20% likelihood. Weekends: +25% probability. Over 13 weeks, linearly increase average weekly episodes by 2 from day 1 to 80, then stable.",
    "characteristics": {
      "required": [
        "id",
        "type",
        "starttime",
        "endtime",
        "duration",
        "steps"
      ],
      "optional": [
        "distance"
      ]
    },
    "temporal_constraints": {
      "per_event_duration": {
        "min": 10,
        "max": 60,
        "unit": "minutes"
      },
      "total_event_duration": {
        "scale": "day",
        "min": 1,
        "max": 4,
        "unit": "hours"
      },
      "total_event_episodes": {
        "scale": "day",
        "min": 2,
        "max": 8,
        "unit": "number"
      },
      "temporal_patterns": [
        {
          "mode": "seasonality",
          "details": {
            "scale": "morning",
            "direction": "increasing",
            "amount": 20,
            "unit": "percentage",
            "within": "morning"
          }
        },
        {
          "mode": "seasonality",
          "details": {
            "scale": "weekend",
            "direction": "increasing",
            "amount": 25,
            "unit": "percentage",
            "within": [
              "Saturday",
              "Sunday"
            ]
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "increasing",
            "amount": 2,
            "unit": "number",
            "within": "80 days",
            "start": 1,
            "end": 80
          }
        }
      ]
    }
  },
  {
    "event_name": "raining",
    "source": "unknown",
    "description": "Raining episodes per participant per day, 0-12 times, each 0-60 minutes, total 0-4 hours/day. Morning: +20% likelihood. Over first 80 days, linearly reduce expected weekly rain episodes by 3.",
    "characteristics": {
      "required": [
        "id",
        "type",
        "starttime",
        "endtime",
        "duration"
      ],
      "optional": [
        "precipitation"
      ]
    },
    "temporal_constraints": {
      "per_event_duration": {
        "min": 0,
        "max": 60,
        "unit": "minutes"
      },
      "total_event_duration": {
        "scale": "day",
        "min": 0,
        "max": 4,
        "unit": "hours"
      },
      "total_event_episodes": {
        "scale": "day",
        "min": 0,
        "max": 12,
        "unit": "number"
      },
      "temporal_patterns": [
        {
          "mode": "seasonality",
          "details": {
            "scale": "morning",
            "direction": "increasing",
            "amount": 20,
            "unit": "percentage",
            "within": "morning"
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "decreasing",
            "amount": 3,
            "unit": "number",
            "within": "80 days",
            "start": 1,
            "end": 80
          }
        }
      ]
    }
  },
  {
    "event_name": "smoking",
    "source": "unknown",
    "description": "Smoking episodes per participant per day, up to 22 times, each 10 minutes, total 0-5 hours/day. Morning: +20% likelihood. Weekend: +10% episodes. Over 13 weeks, episode count: days 1-7 decrease by 8, days 8-22 increase by 1, days 23-37 decrease by 1, days 38-52 increase by 3, days 53-67 decrease by 1, days 68-89 increase by 5.",
    "characteristics": {
      "required": [
        "id",
        "type",
        "starttime",
        "endtime",
        "duration"
      ],
      "optional": []
    },
    "temporal_constraints": {
      "per_event_duration": {
        "min": 10,
        "max": 10,
        "unit": "minutes"
      },
      "total_event_duration": {
        "scale": "day",
        "min": 0,
        "max": 5,
        "unit": "hours"
      },
      "total_event_episodes": {
        "scale": "day",
        "min": 0,
        "max": 22,
        "unit": "number"
      },
      "temporal_patterns": [
        {
          "mode": "seasonality",
          "details": {
            "scale": "morning",
            "direction": "increasing",
            "amount": 20,
            "unit": "percentage",
            "within": "morning"
          }
        },
        {
          "mode": "seasonality",
          "details": {
            "scale": "weekend",
            "direction": "increasing",
            "amount": 10,
            "unit": "percentage",
            "within": [
              "Saturday",
              "Sunday"
            ]
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "decreasing",
            "amount": 8,
            "unit": "number",
            "within": "7 days",
            "start": 1,
            "end": 7
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "increasing",
            "amount": 1,
            "unit": "number",
            "within": "15 days",
            "start": 8,
            "end": 22
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "decreasing",
            "amount": 1,
            "unit": "number",
            "within": "15 days",
            "start": 23,
            "end": 37
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "increasing",
            "amount": 3,
            "unit": "number",
            "within": "15 days",
            "start": 38,
            "end": 52
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "decreasing",
            "amount": 1,
            "unit": "number",
            "within": "15 days",
            "start": 53,
            "end": 67
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "increasing",
            "amount": 5,
            "unit": "number",
            "within": "22 days",
            "start": 68,
            "end": 89
          }
        }
      ]
    }
  },
  {
    "event_name": "stress",
    "source": "unknown",
    "description": "Stress episodes per participant per day, 2-8 times, each 10-30 minutes, total 0-4 hours/day. Morning: +20% likelihood. Days 1-30: increase average by 3, day 40: decrease by 2 over 10 days, days 55-65: decrease by 1, then stable.",
    "characteristics": {
      "required": [
        "id",
        "type",
        "starttime",
        "endtime",
        "duration"
      ],
      "optional": []
    },
    "temporal_constraints": {
      "per_event_duration": {
        "min": 10,
        "max": 30,
        "unit": "minutes"
      },
      "total_event_duration": {
        "scale": "day",
        "min": 0,
        "max": 4,
        "unit": "hours"
      },
      "total_event_episodes": {
        "scale": "day",
        "min": 2,
        "max": 8,
        "unit": "number"
      },
      "temporal_patterns": [
        {
          "mode": "seasonality",
          "details": {
            "scale": "morning",
            "direction": "increasing",
            "amount": 20,
            "unit": "percentage",
            "within": "morning"
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "increasing",
            "amount": 3,
            "unit": "number",
            "within": "30 days",
            "start": 1,
            "end": 30
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "decreasing",
            "amount": 2,
            "unit": "number",
            "within": "10 days",
            "start": 40,
            "end": 49
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "decreasing",
            "amount": 1,
            "unit": "number",
            "within": "11 days",
            "start": 55,
            "end": 65
          }
        }
      ]
    }
  }
]
ltl_expressions = [
  "G \u00ac(long_sleep \u2227 smoking)",
  "G \u00ac(long_sleep \u2227 walking)",
  "G \u00ac(long_sleep \u2227 working)",
  "G \u00ac(long_sleep \u2227 stress)",
  "G \u00ac(walking \u2227 working)",
  "G \u00ac(raining \u2227 smoking)",
  "G \u00ac(walking \u2227 stress)",
  "G (stress \u2192 F smoking)",
  "G (working \u2192 F walking)",
  "G (walking \u2192 F stress)",
  "G (working \u2192 F (working \u2227 stress))"
]
constant_persona_features = {
  "sample_size": 25,
  "horizon": {
    "weeks": 13
  },
  "age_group": "46-63",
  "gender": {
    "male": 0.575,
    "female": 0.425
  },
  "education_level": {
    "high_school": 0.2,
    "bachelor": 0.4,
    "master": 0.3,
    "doctorate and above": 0.1
  },
  "occupation_status": {
    "unemployed": 0.1,
    "parttime": 0.4,
    "fulltime": 0.4,
    "self-employed": 0.1
  },
  "marital_status": {
    "single": 0.1,
    "married": 0.5,
    "engaged": 0.3,
    "divorced": 0.1,
    "separated": 0.0,
    "widowed": 0.0
  },
  "standard": {
    "morning": [
      300,
      600
    ],
    "afternoon": [
      600,
      960
    ],
    "evening": [
      960,
      1200
    ],
    "night": [
      1200,
      1440
    ]
  }
}
