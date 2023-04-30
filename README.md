# Сериализация и десериализация данных через прокси-сервер

Чтобы получить время сериализации и десереализации для каждого формата, нужно выполнить один из запросов:
```console
$ echo -n 'get_result native' | nc -u -w1 0.0.0.0 2000
$ echo -n 'get_result xml' | nc -u -w1 0.0.0.0 2000
$ echo -n 'get_result json' | nc -u -w1 0.0.0.0 2000
$ echo -n 'get_result proto' | nc -u -w1 0.0.0.0 2000
$ echo -n 'get_result avro' | nc -u -w1 0.0.0.0 2000
$ echo -n 'get_result yaml' | nc -u -w2 0.0.0.0 2000
$ echo -n 'get_result msgpack' | nc -u -w1 0.0.0.0 2000
```