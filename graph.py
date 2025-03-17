import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt
import pandas as pd
import mplfinance as mpf
import matplotlib.pyplot as plt

def test1():
    # Пример данных: Дата, Open, High, Low, Close
    data = {
    'Date': ['2023-10-01', '2023-10-02', '2023-10-03', '2023-10-04', '2023-10-05'],
    'Open': [100, 105, 110, 108, 112],
    'High': [102, 108, 112, 111, 115],
    'Low': [98, 103, 107, 106, 110],
    'Close': [101, 107, 109, 110, 113]
    }

    # Преобразуем данные в DataFrame
    df = pd.DataFrame(data)
    df['Color'] = df.apply(lambda row: 'Зелёная' if row['Close'] > row['Open'] else 'Красная', axis=1)


    # Преобразуем столбец 'Date' в тип datetime и устанавливаем его как индекс
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)

    # Построение свечного графика
    mpf.plot(df, type='candle', style='charles', title='Свечной график', ylabel='Цена')


    # Выводим цвет первой свечи
    first_candle_color = df.loc[0, 'Color']
    print(f"Цвет первой свечи: {first_candle_color}")

def test2():
    # Пример данных для первого графика
    x1 = [1, 2, 3, 4, 5]
    y1 = [2, 3, 5, 7, 11]

    # Пример данных для второго графика
    x2 = [1, 2, 3, 4, 5]
    y2 = [1, 4, 6, 8, 10]

    # Построение графиков
    plt.plot(x1, y1, label='График 1', marker='o')
    plt.plot(x2, y2, label='График 2', marker='x')

    # Добавление подписей
    plt.title('Сравнение двух графиков')
    plt.xlabel('Ось X')
    plt.ylabel('Ось Y')
    plt.legend()

    # Отображение графика
    plt.show()

def test3():
    data1 = {
    'Date': ['2023-10-01', '2023-10-02', '2023-10-03', '2023-10-04', '2023-10-05'],
    'Open': [100, 105, 110, 108, 112],
    'High': [102, 108, 112, 111, 115],
    'Low': [98, 103, 107, 106, 110],
    'Close': [101, 107, 109, 110, 113]
    }

    # Пример данных для второго графика
    data2 = {
        'Date': ['2023-10-01', '2023-10-02', '2023-10-03', '2023-10-04', '2023-10-05'],
        'Open': [101, 104, 109, 107, 111],
        'High': [103, 107, 111, 110, 114],
        'Low': [99, 102, 106, 105, 109],
        'Close': [102, 106, 108, 109, 112]
    }

    # Преобразуем данные в DataFrame
    df1 = pd.DataFrame(data1)
    df2 = pd.DataFrame(data2)

    # Преобразуем столбец 'Date' в тип datetime и устанавливаем его как индекс
    df1['Date'] = pd.to_datetime(df1['Date'])
    df1.set_index('Date', inplace=True)

    df2['Date'] = pd.to_datetime(df2['Date'])
    df2.set_index('Date', inplace=True)

    # Создаем фигуру с двумя подграфиками
    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    # Построение первого свечного графика
    mpf.plot(df1, type='candle', style='charles', ax=axes[0], title='Свечной график 1')

    # Построение второго свечного графика
    mpf.plot(df2, type='candle', style='charles', ax=axes[1], title='Свечной график 2')

    # Отображение графиков
    plt.tight_layout()
    plt.show()

test1()