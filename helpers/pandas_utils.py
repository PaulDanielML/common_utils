import pandas as pd

__all__ = ["detailed_df_info"]


def detailed_df_info(df: pd.DataFrame) -> pd.DataFrame:
    ex_vals = []
    for c in df:
        if not (non_nans := df.loc[~df[c].isna(), c]).empty:
            ex_vals.append(non_nans.sample(1).item())
        else:
            ex_vals.append(df[c].sample(1).item())
    return pd.concat(
        [
            df.dtypes.rename("DType"),
            (df.memory_usage(deep=True) / (2 ** 20)).rename("Mem usage [MB]"),
            pd.Series(ex_vals, index=df.columns).rename("Example value"),
            df.isna().sum().rename("Number NaNs"),
        ],
        axis=1,
    ).rename_axis("Column", axis=1)
