Comment Plugin
==============

### API

* POST /thread

      Response:
      { "tid": "900000000000000001" }

* GET /thread/:tid
* GET /thread/:tid?since=:cid

      Response:
      [ { "tid": "900000000000000001",
          "cid": "1000000000000000013",
          "user": "wizawu",
          "time": 1423554286268,
          "body": "Hello, world"
        },
        { "tid": "900000000000000001",
          "cid": "1000000000000000016",
          ......
        },
        ......
      ]

* GET /comment/:cid

      Response:
      { "tid": "900000000000000001",
        "cid": "1000000000000000013",
        "user": "wizawu",
        "time": 1423554286268,
        "body": "Hello, world"
      }

* POST /comment

      Request:
      { "tid": "900000000000000001",
        "body": "Hello, world"
      }

      Response:
      { "cid": "1000000000000000017" }

* DELETE /comment/:cid
