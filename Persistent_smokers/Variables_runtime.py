eventironmental_data = [
  {
    "event_name": "long_sleep",
    "source": "unknown",
    "description": "A single, long sleep episode per participant per day, typically starting at night between 20:00 and 24:00, lasting 6-9 hours.",
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
    "description": "Work episodes occurring twice per weekday (Monday-Friday), each lasting 3-5 hours, for a total of 6-9 hours per day, only in the morning and afternoon.",
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
    "description": "Walking episodes, 2-8 per day, each lasting 10-60 minutes, totaling 1-4 hours per day. Increased likelihood in the morning (+20%) and on weekends (+25%). Over 13 weeks, weekly walking episodes increase by 2 from day 1 to 80, then stabilize.",
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
    "description": "Rain episodes, 0-12 per day, each lasting 0-60 minutes, totaling 0-4 hours per day. Morning rain is 20% more likely. Over the first 80 days, weekly rain episodes decrease by 3.",
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
    "description": "Smoking episodes, up to 40 per day, each lasting 10 minutes, totaling up to 5 hours per day. Morning episodes are 20% more likely, weekends have 10% more episodes. Over 13 weeks, episode count varies: days 1-7 decrease by 8, days 8-15 increase by 3, days 16-23 decrease by 2, days 24-31 increase by 1, days 32-46 decrease by 4, days 46-68 increase by 2, days 69-90 decrease by 7.",
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
        "max": 40,
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
            "amount": 3,
            "unit": "number",
            "within": "8 days",
            "start": 8,
            "end": 15
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "decreasing",
            "amount": 2,
            "unit": "number",
            "within": "8 days",
            "start": 16,
            "end": 23
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "increasing",
            "amount": 1,
            "unit": "number",
            "within": "8 days",
            "start": 24,
            "end": 31
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "decreasing",
            "amount": 4,
            "unit": "number",
            "within": "15 days",
            "start": 32,
            "end": 46
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "increasing",
            "amount": 2,
            "unit": "number",
            "within": "23 days",
            "start": 46,
            "end": 68
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "decreasing",
            "amount": 7,
            "unit": "number",
            "within": "22 days",
            "start": 69,
            "end": 90
          }
        }
      ]
    }
  },
  {
    "event_name": "stress",
    "source": "unknown",
    "description": "Stress episodes, 2-8 per day, each lasting 10-30 minutes, totaling up to 4 hours per day. Morning episodes are 20% more likely. From day 0-90, decrease by 2 events, then stabilize.",
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
            "direction": "decreasing",
            "amount": 2,
            "unit": "number",
            "within": "90 days",
            "start": 0,
            "end": 90
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
  "age_group": "43-62",
  "gender": {
    "male": 0.575,
    "female": 0.425
  },
  "education_level": {
    "high-school": 0.6,
    "bachelor": 0.3,
    "master": 0.1,
    "doctorate and above": 0.0
  },
  "occupation_status": {
    "unemployed": 0.3,
    "parttime": 0.4,
    "fulltime": 0.3,
    "self-employed": 0.0
  },
  "marital_status": {
    "single": 0.45,
    "married": 0.15,
    "engaged": 0.2,
    "divorced": 0.2,
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
