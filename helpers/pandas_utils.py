import pandas as pd

__all__ = ["detailed_df_info"]


def detailed_df_info(df: pd.DataFrame, ex_vals_char_lmt: int = 100) -> pd.DataFrame:
    limit = ex_vals_char_lmt or 10_000
    ex_vals = []
    for c in df:
        if not (non_nans := df.loc[~df[c].isna(), c]).empty:
            val = non_nans.sample(1).item()
            ex_vals.append(
                val[:limit] + " ..." if isinstance(val, str) and (len(val) > limit) else val
            )
        else:
            ex_vals.append(df[c].sample(1).item())
    return (
        pd.concat(
            [
                df.dtypes.rename("DType"),
                (df.memory_usage(deep=True) / (2 ** 20)).rename("Mem usage [MB]"),
                pd.Series(ex_vals, index=df.columns).rename("Example value"),
                (df.isna().sum() / len(df) * 100).astype(int).rename("% NaNs"),
            ],
            axis=1,
        )
        .rename_axis("Column", axis=1)
        .style.background_gradient(axis=0, subset=["% NaNs"], cmap="YlOrRd")
        .format("{:.0f}", subset=["% NaNs"])
        .format("{:.2f}", subset=["Mem usage [MB]"])
        .format(hyperlinks="html", subset=["Example value"])
    )
