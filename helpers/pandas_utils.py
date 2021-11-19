import pandas as pd

__all__ = ["detailed_df_info"]


def detailed_df_info(df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat(
        [
            df.dtypes.rename("DType"),
            (df.memory_usage(deep=True) / (2 ** 20)).rename("Mem usage [MB]"),
        ],
        axis=1,
    ).rename_axis("Column", axis=1)
