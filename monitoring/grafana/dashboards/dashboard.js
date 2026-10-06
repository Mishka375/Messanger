{
  "apiVersion": "dashboard.grafana.app/v2",
  "kind": "Dashboard",
  "metadata": {
    "name": "adscqpc"
  },
  "spec": {
    "annotations": [
      {
        "kind": "AnnotationQuery",
        "spec": {
          "builtIn": true,
          "enable": true,
          "hide": true,
          "iconColor": "rgba(0, 211, 255, 1)",
          "name": "Annotations & Alerts",
          "query": {
            "datasource": {
              "name": "-- Grafana --"
            },
            "group": "grafana",
            "kind": "DataQuery",
            "spec": {},
            "version": "v0"
          }
        }
      }
    ],
    "cursorSync": "Off",
    "editable": true,
    "elements": {
      "panel-1": {
        "kind": "Panel",
        "spec": {
          "data": {
            "kind": "QueryGroup",
            "spec": {
              "queries": [
                {
                  "kind": "PanelQuery",
                  "spec": {
                    "hidden": false,
                    "query": {
                      "datasource": {
                        "name": "PBFA97CFB590B2093"
                      },
                      "group": "prometheus",
                      "kind": "DataQuery",
                      "spec": {
                        "editorMode": "builder",
                        "expr": "users_total",
                        "legendFormat": "__auto",
                        "range": true
                      },
                      "version": "v0"
                    },
                    "refId": "A"
                  }
                }
              ],
              "queryOptions": {},
              "transformations": []
            }
          },
          "description": "",
          "id": 1,
          "links": [],
          "title": "Users total",
          "vizConfig": {
            "group": "timeseries",
            "kind": "VizConfig",
            "spec": {
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "barWidthFactor": 0.6,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "showValues": false,
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": 0
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  }
                },
                "overrides": []
              },
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "hideZeros": false,
                  "mode": "single",
                  "sort": "none"
                }
              }
            },
            "version": "13.2.2"
          }
        }
      },
      "panel-10": {
        "kind": "Panel",
        "spec": {
          "data": {
            "kind": "QueryGroup",
            "spec": {
              "queries": [
                {
                  "kind": "PanelQuery",
                  "spec": {
                    "hidden": false,
                    "query": {
                      "datasource": {
                        "name": "PBFA97CFB590B2093"
                      },
                      "group": "prometheus",
                      "kind": "DataQuery",
                      "spec": {
                        "editorMode": "builder",
                        "expr": "sql_request_errors_total",
                        "legendFormat": "__auto",
                        "range": true
                      },
                      "version": "v0"
                    },
                    "refId": "A"
                  }
                }
              ],
              "queryOptions": {},
              "transformations": []
            }
          },
          "description": "",
          "id": 10,
          "links": [],
          "title": "SQL request error",
          "vizConfig": {
            "group": "timeseries",
            "kind": "VizConfig",
            "spec": {
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "barWidthFactor": 0.6,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "showValues": false,
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": 0
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  }
                },
                "overrides": []
              },
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "hideZeros": false,
                  "mode": "single",
                  "sort": "none"
                }
              }
            },
            "version": "13.2.2"
          }
        }
      },
      "panel-11": {
        "kind": "Panel",
        "spec": {
          "data": {
            "kind": "QueryGroup",
            "spec": {
              "queries": [
                {
                  "kind": "PanelQuery",
                  "spec": {
                    "hidden": false,
                    "query": {
                      "datasource": {
                        "name": "PBFA97CFB590B2093"
                      },
                      "group": "prometheus",
                      "kind": "DataQuery",
                      "spec": {
                        "editorMode": "builder",
                        "expr": "redis_errors_count_total",
                        "legendFormat": "__auto",
                        "range": true
                      },
                      "version": "v0"
                    },
                    "refId": "A"
                  }
                }
              ],
              "queryOptions": {},
              "transformations": []
            }
          },
          "description": "",
          "id": 11,
          "links": [],
          "title": "Redis request error",
          "vizConfig": {
            "group": "timeseries",
            "kind": "VizConfig",
            "spec": {
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "barWidthFactor": 0.6,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "showValues": false,
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": 0
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  }
                },
                "overrides": []
              },
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "hideZeros": false,
                  "mode": "single",
                  "sort": "none"
                }
              }
            },
            "version": "13.2.2"
          }
        }
      },
      "panel-12": {
        "kind": "Panel",
        "spec": {
          "data": {
            "kind": "QueryGroup",
            "spec": {
              "queries": [
                {
                  "kind": "PanelQuery",
                  "spec": {
                    "hidden": false,
                    "query": {
                      "datasource": {
                        "name": "PBFA97CFB590B2093"
                      },
                      "group": "prometheus",
                      "kind": "DataQuery",
                      "spec": {
                        "editorMode": "builder",
                        "expr": "request_errors_total",
                        "legendFormat": "__auto",
                        "range": true
                      },
                      "version": "v0"
                    },
                    "refId": "A"
                  }
                }
              ],
              "queryOptions": {},
              "transformations": []
            }
          },
          "description": "",
          "id": 12,
          "links": [],
          "title": "Request errors",
          "vizConfig": {
            "group": "timeseries",
            "kind": "VizConfig",
            "spec": {
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "barWidthFactor": 0.6,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "showValues": false,
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": 0
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  }
                },
                "overrides": []
              },
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "hideZeros": false,
                  "mode": "single",
                  "sort": "none"
                }
              }
            },
            "version": "13.2.2"
          }
        }
      },
      "panel-13": {
        "kind": "Panel",
        "spec": {
          "data": {
            "kind": "QueryGroup",
            "spec": {
              "queries": [
                {
                  "kind": "PanelQuery",
                  "spec": {
                    "hidden": false,
                    "query": {
                      "datasource": {
                        "name": "PBFA97CFB590B2093"
                      },
                      "group": "prometheus",
                      "kind": "DataQuery",
                      "spec": {
                        "editorMode": "builder",
                        "expr": "request_time_bucket",
                        "legendFormat": "__auto",
                        "range": true
                      },
                      "version": "v0"
                    },
                    "refId": "A"
                  }
                }
              ],
              "queryOptions": {},
              "transformations": []
            }
          },
          "description": "",
          "id": 13,
          "links": [],
          "title": "Request time",
          "vizConfig": {
            "group": "table",
            "kind": "VizConfig",
            "spec": {
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "thresholds"
                  },
                  "custom": {
                    "align": "left",
                    "cellOptions": {
                      "type": "json-view"
                    },
                    "filterable": false,
                    "footer": {
                      "reducers": [
                        "lastNotNull",
                        "max",
                        "min"
                      ]
                    },
                    "inspect": false,
                    "styleField": "Time",
                    "wrapHeaderText": false,
                    "wrapText": false
                  },
                  "fieldMinMax": false,
                  "thresholds": {
                    "mode": "percentage",
                    "steps": [
                      {
                        "color": "green",
                        "value": 0
                      },
                      {
                        "color": "orange",
                        "value": 60
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  }
                },
                "overrides": []
              },
              "options": {
                "cellHeight": "sm",
                "enablePagination": false,
                "frameIndex": 0,
                "showHeader": true
              }
            },
            "version": "13.2.2"
          }
        }
      },
      "panel-14": {
        "kind": "Panel",
        "spec": {
          "data": {
            "kind": "QueryGroup",
            "spec": {
              "queries": [
                {
                  "kind": "PanelQuery",
                  "spec": {
                    "hidden": false,
                    "query": {
                      "group": "",
                      "kind": "DataQuery",
                      "spec": {},
                      "version": "v0"
                    },
                    "refId": "A"
                  }
                }
              ],
              "queryOptions": {},
              "transformations": []
            }
          },
          "description": "",
          "id": 14,
          "links": [],
          "title": "New panel",
          "vizConfig": {
            "group": "__unconfigured-panel",
            "kind": "VizConfig",
            "spec": {
              "fieldConfig": {
                "defaults": {},
                "overrides": []
              },
              "options": {}
            },
            "version": "13.2.2"
          }
        }
      },
      "panel-3": {
        "kind": "Panel",
        "spec": {
          "data": {
            "kind": "QueryGroup",
            "spec": {
              "queries": [
                {
                  "kind": "PanelQuery",
                  "spec": {
                    "hidden": false,
                    "query": {
                      "datasource": {
                        "name": "PBFA97CFB590B2093"
                      },
                      "group": "prometheus",
                      "kind": "DataQuery",
                      "spec": {
                        "editorMode": "builder",
                        "expr": "users_online",
                        "legendFormat": "__auto",
                        "range": true
                      },
                      "version": "v0"
                    },
                    "refId": "A"
                  }
                }
              ],
              "queryOptions": {},
              "transformations": []
            }
          },
          "description": "",
          "id": 3,
          "links": [],
          "title": "Users online",
          "vizConfig": {
            "group": "timeseries",
            "kind": "VizConfig",
            "spec": {
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "barWidthFactor": 0.6,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "showValues": false,
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": 0
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  }
                },
                "overrides": []
              },
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "hideZeros": false,
                  "mode": "single",
                  "sort": "none"
                }
              }
            },
            "version": "13.2.2"
          }
        }
      },
      "panel-4": {
        "kind": "Panel",
        "spec": {
          "data": {
            "kind": "QueryGroup",
            "spec": {
              "queries": [
                {
                  "kind": "PanelQuery",
                  "spec": {
                    "hidden": false,
                    "query": {
                      "datasource": {
                        "name": "PBFA97CFB590B2093"
                      },
                      "group": "prometheus",
                      "kind": "DataQuery",
                      "spec": {
                        "editorMode": "builder",
                        "expr": "up",
                        "legendFormat": "__auto",
                        "range": true
                      },
                      "version": "v0"
                    },
                    "refId": "A"
                  }
                }
              ],
              "queryOptions": {},
              "transformations": []
            }
          },
          "description": "",
          "id": 4,
          "links": [],
          "title": "Status",
          "vizConfig": {
            "group": "stat",
            "kind": "VizConfig",
            "spec": {
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "thresholds"
                  },
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": 0
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  }
                },
                "overrides": []
              },
              "options": {
                "colorMode": "value",
                "graphMode": "area",
                "justifyMode": "auto",
                "orientation": "auto",
                "percentChangeColorMode": "standard",
                "reduceOptions": {
                  "calcs": [
                    "lastNotNull"
                  ],
                  "fields": "",
                  "values": false
                },
                "showPercentChange": false,
                "textMode": "auto",
                "wideLayout": true
              }
            },
            "version": "13.2.2"
          }
        }
      },
      "panel-6": {
        "kind": "Panel",
        "spec": {
          "data": {
            "kind": "QueryGroup",
            "spec": {
              "queries": [
                {
                  "kind": "PanelQuery",
                  "spec": {
                    "hidden": false,
                    "query": {
                      "group": "",
                      "kind": "DataQuery",
                      "spec": {},
                      "version": "v0"
                    },
                    "refId": "A"
                  }
                }
              ],
              "queryOptions": {},
              "transformations": []
            }
          },
          "description": "",
          "id": 6,
          "links": [],
          "title": "Redis request queue",
          "vizConfig": {
            "group": "__unconfigured-panel",
            "kind": "VizConfig",
            "spec": {
              "fieldConfig": {
                "defaults": {},
                "overrides": []
              },
              "options": {}
            },
            "version": "13.2.2"
          }
        }
      },
      "panel-7": {
        "kind": "Panel",
        "spec": {
          "data": {
            "kind": "QueryGroup",
            "spec": {
              "queries": [
                {
                  "kind": "PanelQuery",
                  "spec": {
                    "hidden": false,
                    "query": {
                      "datasource": {
                        "name": "PBFA97CFB590B2093"
                      },
                      "group": "prometheus",
                      "kind": "DataQuery",
                      "spec": {
                        "editorMode": "builder",
                        "expr": "sql_request_queue",
                        "legendFormat": "__auto",
                        "range": true
                      },
                      "version": "v0"
                    },
                    "refId": "A"
                  }
                }
              ],
              "queryOptions": {},
              "transformations": []
            }
          },
          "description": "",
          "id": 7,
          "links": [],
          "title": "SQL request queue",
          "vizConfig": {
            "group": "timeseries",
            "kind": "VizConfig",
            "spec": {
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "barWidthFactor": 0.6,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "showValues": false,
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": 0
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  }
                },
                "overrides": []
              },
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "hideZeros": false,
                  "mode": "single",
                  "sort": "none"
                }
              }
            },
            "version": "13.2.2"
          }
        }
      },
      "panel-8": {
        "kind": "Panel",
        "spec": {
          "data": {
            "kind": "QueryGroup",
            "spec": {
              "queries": [
                {
                  "kind": "PanelQuery",
                  "spec": {
                    "hidden": false,
                    "query": {
                      "datasource": {
                        "name": "PBFA97CFB590B2093"
                      },
                      "group": "prometheus",
                      "kind": "DataQuery",
                      "spec": {
                        "editorMode": "builder",
                        "expr": "sql_request_count_total",
                        "legendFormat": "__auto",
                        "range": true
                      },
                      "version": "v0"
                    },
                    "refId": "A"
                  }
                }
              ],
              "queryOptions": {},
              "transformations": []
            }
          },
          "description": "",
          "id": 8,
          "links": [],
          "title": "SQL request count",
          "vizConfig": {
            "group": "timeseries",
            "kind": "VizConfig",
            "spec": {
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "barWidthFactor": 0.6,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "showValues": false,
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": 0
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  }
                },
                "overrides": []
              },
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "hideZeros": false,
                  "mode": "single",
                  "sort": "none"
                }
              }
            },
            "version": "13.2.2"
          }
        }
      },
      "panel-9": {
        "kind": "Panel",
        "spec": {
          "data": {
            "kind": "QueryGroup",
            "spec": {
              "queries": [
                {
                  "kind": "PanelQuery",
                  "spec": {
                    "hidden": false,
                    "query": {
                      "datasource": {
                        "name": "PBFA97CFB590B2093"
                      },
                      "group": "prometheus",
                      "kind": "DataQuery",
                      "spec": {
                        "editorMode": "builder",
                        "expr": "request_count_total",
                        "legendFormat": "__auto",
                        "range": true
                      },
                      "version": "v0"
                    },
                    "refId": "A"
                  }
                }
              ],
              "queryOptions": {},
              "transformations": []
            }
          },
          "description": "",
          "id": 9,
          "links": [],
          "title": "Redis request count",
          "vizConfig": {
            "group": "timeseries",
            "kind": "VizConfig",
            "spec": {
              "fieldConfig": {
                "defaults": {
                  "color": {
                    "mode": "palette-classic"
                  },
                  "custom": {
                    "axisBorderShow": false,
                    "axisCenteredZero": false,
                    "axisColorMode": "text",
                    "axisLabel": "",
                    "axisPlacement": "auto",
                    "barAlignment": 0,
                    "barWidthFactor": 0.6,
                    "drawStyle": "line",
                    "fillOpacity": 0,
                    "gradientMode": "none",
                    "hideFrom": {
                      "legend": false,
                      "tooltip": false,
                      "viz": false
                    },
                    "insertNulls": false,
                    "lineInterpolation": "linear",
                    "lineWidth": 1,
                    "pointSize": 5,
                    "scaleDistribution": {
                      "type": "linear"
                    },
                    "showPoints": "auto",
                    "showValues": false,
                    "spanNulls": false,
                    "stacking": {
                      "group": "A",
                      "mode": "none"
                    },
                    "thresholdsStyle": {
                      "mode": "off"
                    }
                  },
                  "thresholds": {
                    "mode": "absolute",
                    "steps": [
                      {
                        "color": "green",
                        "value": 0
                      },
                      {
                        "color": "red",
                        "value": 80
                      }
                    ]
                  }
                },
                "overrides": []
              },
              "options": {
                "legend": {
                  "calcs": [],
                  "displayMode": "list",
                  "placement": "bottom",
                  "showLegend": true
                },
                "tooltip": {
                  "hideZeros": false,
                  "mode": "single",
                  "sort": "none"
                }
              }
            },
            "version": "13.2.2"
          }
        }
      }
    },
    "layout": {
      "kind": "RowsLayout",
      "spec": {
        "rows": [
          {
            "kind": "RowsLayoutRow",
            "spec": {
              "collapse": false,
              "layout": {
                "kind": "GridLayout",
                "spec": {
                  "items": [
                    {
                      "kind": "GridLayoutItem",
                      "spec": {
                        "element": {
                          "kind": "ElementReference",
                          "name": "panel-1"
                        },
                        "height": 8,
                        "width": 12,
                        "x": 0,
                        "y": 0
                      }
                    },
                    {
                      "kind": "GridLayoutItem",
                      "spec": {
                        "element": {
                          "kind": "ElementReference",
                          "name": "panel-4"
                        },
                        "height": 16,
                        "width": 12,
                        "x": 12,
                        "y": 0
                      }
                    },
                    {
                      "kind": "GridLayoutItem",
                      "spec": {
                        "element": {
                          "kind": "ElementReference",
                          "name": "panel-3"
                        },
                        "height": 8,
                        "width": 12,
                        "x": 0,
                        "y": 8
                      }
                    },
                    {
                      "kind": "GridLayoutItem",
                      "spec": {
                        "element": {
                          "kind": "ElementReference",
                          "name": "panel-10"
                        },
                        "height": 8,
                        "width": 12,
                        "x": 0,
                        "y": 16
                      }
                    },
                    {
                      "kind": "GridLayoutItem",
                      "spec": {
                        "element": {
                          "kind": "ElementReference",
                          "name": "panel-11"
                        },
                        "height": 8,
                        "width": 12,
                        "x": 12,
                        "y": 16
                      }
                    },
                    {
                      "kind": "GridLayoutItem",
                      "spec": {
                        "element": {
                          "kind": "ElementReference",
                          "name": "panel-7"
                        },
                        "height": 8,
                        "width": 12,
                        "x": 0,
                        "y": 24
                      }
                    },
                    {
                      "kind": "GridLayoutItem",
                      "spec": {
                        "element": {
                          "kind": "ElementReference",
                          "name": "panel-6"
                        },
                        "height": 8,
                        "width": 12,
                        "x": 12,
                        "y": 24
                      }
                    },
                    {
                      "kind": "GridLayoutItem",
                      "spec": {
                        "element": {
                          "kind": "ElementReference",
                          "name": "panel-8"
                        },
                        "height": 8,
                        "width": 12,
                        "x": 0,
                        "y": 32
                      }
                    },
                    {
                      "kind": "GridLayoutItem",
                      "spec": {
                        "element": {
                          "kind": "ElementReference",
                          "name": "panel-9"
                        },
                        "height": 8,
                        "width": 12,
                        "x": 12,
                        "y": 32
                      }
                    },
                    {
                      "kind": "GridLayoutItem",
                      "spec": {
                        "element": {
                          "kind": "ElementReference",
                          "name": "panel-12"
                        },
                        "height": 8,
                        "width": 12,
                        "x": 0,
                        "y": 40
                      }
                    },
                    {
                      "kind": "GridLayoutItem",
                      "spec": {
                        "element": {
                          "kind": "ElementReference",
                          "name": "panel-13"
                        },
                        "height": 16,
                        "width": 12,
                        "x": 12,
                        "y": 40
                      }
                    },
                    {
                      "kind": "GridLayoutItem",
                      "spec": {
                        "element": {
                          "kind": "ElementReference",
                          "name": "panel-14"
                        },
                        "height": 8,
                        "width": 12,
                        "x": 0,
                        "y": 48
                      }
                    }
                  ]
                }
              },
              "title": "New row"
            }
          }
        ]
      }
    },
    "links": [],
    "liveNow": false,
    "preferences": {
      "layout": {
        "kind": "GridLayout",
        "spec": {
          "items": []
        }
      }
    },
    "preload": false,
    "tags": [],
    "timeSettings": {
      "autoRefresh": "auto",
      "autoRefreshIntervals": [
        "5s",
        "10s",
        "30s",
        "1m",
        "5m",
        "15m",
        "30m",
        "1h",
        "2h",
        "1d"
      ],
      "fiscalYearStartMonth": 0,
      "from": "now-5m",
      "hideTimepicker": false,
      "timezone": "browser",
      "to": "now"
    },
    "title": "Main",
    "variables": []
  }
}
