Comment Plugin
==============

### Install

```
sudo apt-get install python3 python3-pip redis-server
sudo pip3 install -r requirements.txt

# Start app
./app.py
```

### Usage

```
<link rel="import" href="/comment/elements/thread-element.html">

<thread-element key="task/issues/123"></thread-element>
```

### API

* POST `/threads`
* POST `/threads?key=:key`
    ```
    # Response
    { "tid": "900000000000000001" }
    ```

* GET `/threads/:tid`
* GET `/threads/:tid?since=:cid`
    ```
    # Response
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
    ```

* GET `/comments/:cid`
    ```
    # Response
    { "tid": "900000000000000001",
      "cid": "1000000000000000013",
      "user": "wizawu",
      "time": 1423554286268,
      "body": "Hello, world"
    }
    ```

* POST `/comments`
    ```
    # Request
    { "tid": "900000000000000001",
      "body": "Hello, world"
    }

    # Response
    { "cid": "1000000000000000017" }
    ```

* DELETE `/comments/:cid`
