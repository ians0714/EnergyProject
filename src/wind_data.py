import pandas as pd


WIND_DATA_PATH = (
    r"C:\Users\admin\PycharmProjects\EnergyProject\data\ninja-wind-country-DE-current_onshore-merra2 - 2023.csv"
)


def load_wind_data():
    df = pd.read_csv(WIND_DATA_PATH)

    # 필요한 열만 사용
    df = df[["time", "NATIONAL"]].copy()

    # 이름 정리
    df = df.rename(
        columns={
            "NATIONAL": "Wind_Capacity_Factor"
        }
    )

    # 시간 형식 변환
    df["time"] = pd.to_datetime(
        df["time"],
        utc=True
    )

    # 시간 순서 정렬
    df = df.sort_values("time")

    # index 초기화
    df = df.reset_index(drop=True)

    return df

wind_data = load_wind_data()
wind_data.set_index("time", inplace=True)

if __name__ == "__main__":
    print(wind_data.head())
    print(wind_data.tail())
    print("\nNumber of hours:", len(wind_data))
    print(
        "Wind CF range:",
        wind_data["Wind_Capacity_Factor"].min(),
        "-",
        wind_data["Wind_Capacity_Factor"].max()
    )