import pandas as pd

__all__ = ["detailed_df_info"]


def detailed_df_info(df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat(
        [
            df.dtypes.rename("DType"),
            (df.memory_usage(deep=True) / (2 ** 20)).rename("Mem usage [MB]"),
            df.sample(1).squeeze().rename("Example value"),
            df.isna().sum().rename("Number NaNs"),
        ],
        axis=1,
    ).rename_axis("Column", axis=1)

    return df
