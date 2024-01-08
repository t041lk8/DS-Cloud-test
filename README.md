# DS-Cloud-test
Решение тестового задания на позицию Data Scientist в Cloud.ru

## Описание

Была обучена сеть для задачи Named Entity Recognition на датасете [NERUS](https://github.com/natasha/nerus). В качестве модели была выбрана модель ruBERT. От неё я взял токенизатор и энкодер, добавив к ним классификатор для токенов. Поверх обучения использовался *pytorch lightning*, а для логирования - *tensorboard*. В ходе решения тестового задания были реализованы сервисы kserve, jupyter, tensorboard.

___

## Ноутбуки

[Обучение модели](./notebooks/train.ipynb)

[Отправка запросов к kserve](./notebooks/kserve.ipynb)

___

## Использование

1. Загрузите [веса](https://disk.yandex.ru/d/dhE0GWA6eJOcSQ) из облака и распакуйте их в директорию 
```shell 
/DS-Cloud-test/model/ 
```

2.  Запустите все сервисы через докер

```shell
docker compose up
```

3. Для нужного сервиса перейдите по адресу

- [jupyter](http://localhost:8888/lab/tree/notebooks/train.ipynb) для обучения модели
- [jupyter](http://localhost:8888/lab/tree/notebooks/kserve.ipynb) для инференса через kserve
- [tensorboard](http://localhost:6006)

___