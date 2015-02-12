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

* POST `/thread`
* POST `/thread?key=:key`
    ```
    # Response
    { "tid": "900000000000000001" }
    ```

* GET `/thread/:tid`
* GET `/thread/:tid?since=:cid`
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

* GET `/comment/:cid`
    ```
    # Response
    { "tid": "900000000000000001",
      "cid": "1000000000000000013",
      "user": "wizawu",
      "time": 1423554286268,
      "body": "Hello, world"
    }
    ```

* POST `/comment`
    ```
    # Request
    { "tid": "900000000000000001",
      "body": "Hello, world"
    }

    # Response
    { "cid": "1000000000000000017" }
    ```

* DELETE `/comment/:cid`
