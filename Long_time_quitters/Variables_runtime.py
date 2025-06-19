eventironmental_data = [
  {
    "event_name": "long_sleep",
    "source": "wearable",
    "description": "A single, consolidated sleep episode per participant per day, starting during the night (20:00-24:00), lasting between 6 and 9 hours.",
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
    "source": "smartphone",
    "description": "Two work episodes per weekday, each lasting 3-5 hours, with total daily work duration between 6 and 9 hours. Only scheduled in morning and afternoon. No work on weekends.",
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
    "source": "wearable",
    "description": "Walking episodes per participant per day, each lasting 10-60 minutes, with 2-8 episodes per day and total daily walking time between 1 and 4 hours. Morning and weekend walking is more likely. Over 13 weeks, weekly episodes increase by 2 from day 1 to 80, then stabilize.",
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
    "description": "Rain episodes per participant per day, each lasting 0-60 minutes, with 0-12 episodes per day and total daily rain duration between 0 and 4 hours. Morning rain is more likely. Over first 80 days, weekly rain episodes decrease by 3.",
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
    "description": "Smoking episodes per participant per day, up to 22 episodes, each lasting exactly 10 minutes, with total daily smoking duration between 0 and 5 hours. Morning and weekend smoking is more likely. Over 13 weeks, number of episodes varies according to a specified pattern.",
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
            "amount": 10,
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
            "direction": "decreasing",
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
            "direction": "increasing",
            "amount": 5,
            "unit": "number",
            "within": "3 days",
            "start": 16,
            "end": 18
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "decreasing",
            "amount": 4,
            "unit": "number",
            "within": "3 days",
            "start": 20,
            "end": 22
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "increasing",
            "amount": 2,
            "unit": "number",
            "within": "4 days",
            "start": 30,
            "end": 33
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "decreasing",
            "amount": 2,
            "unit": "number",
            "within": "4 days",
            "start": 35,
            "end": 38
          }
        }
      ]
    }
  },
  {
    "event_name": "stress",
    "source": "wearable",
    "description": "Stress episodes per participant per day, 2-8 episodes, each lasting 10-30 minutes, with total daily stress duration between 0 and 4 hours. Morning episodes are more likely. From day 1-20, increase by 3 events; day 21-71, decrease by 4; day 75-85, decrease by 1.",
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
            "within": "20 days",
            "start": 1,
            "end": 20
          }
        },
        {
          "mode": "trend",
          "details": {
            "scale": "season",
            "direction": "decreasing",
            "amount": 4,
            "unit": "number",
            "within": "51 days",
            "start": 21,
            "end": 71
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
            "start": 75,
            "end": 85
          }
        }
      ]
    }
  }
]
ltl_expressions = [
  "G \u00ac(long_sleep \u2227 smoking)",
  "G \u00ac(long_sleep \u2227 walking)",
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
  "age_group": "47-62",
  "gender": {
    "male": 0.6,
    "female": 0.4
  },
  "education_level": {
    "high-school": 0.3,
    "bachelor": 0.3,
    "master": 0.3,
    "doctorate and above": 0.1
  },
  "occupation_status": {
    "unemployed": 0.4,
    "parttime": 0.4,
    "fulltime": 0.1,
    "self-employed": 0.1
  },
  "marital_status": {
    "single": 0.1,
    "married": 0.6,
    "engaged": 0.1,
    "divorced": 0.1,
    "widowed": 0.1
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
