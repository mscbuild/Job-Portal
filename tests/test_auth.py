def test_register(client):
    res = client.post("/register", data={
        "username": "test",
        "password": "123",
        "role": "worker"
    })
    assert res.status_code in [200, 302]
