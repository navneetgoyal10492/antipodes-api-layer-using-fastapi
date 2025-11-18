# app/services/excel_service.py
import pandas as pd
from pandas.tseries.offsets import DateOffset
from pathlib import Path

class ExcelService:
    UPLOAD_DIR = Path("data/uploads")

    # Helper function - to read excel file based on the name.
    @staticmethod
    def read_excel(filename: str) -> pd.DataFrame:
        file_path = ExcelService.UPLOAD_DIR / filename
        if not file_path.exists():
            raise FileNotFoundError(f"{filename} not found in uploads folder.")
        return pd.read_excel(file_path)

    # Helper function - compute compounded return between two dates
    @staticmethod
    def compounded_return(df, start_date, end_date):
        mask = (df["ReturnDate"] > start_date) & (df["ReturnDate"] <= end_date)
        subset = df.loc[mask, "ReturnValue"]
        if subset.empty:
            return None
        return (1 + subset).prod() - 1
    
    @staticmethod
    def generate_returns(df: pd.DataFrame, as_of_date):
        df["ReturnDate"] = pd.to_datetime(df["ReturnDate"])

        df = df.sort_values(["VehicleID", "ReturnDate"])

        # Split into Fund and Benchmark
        fund_df = df[df["VehicleID"] == "FUNDA"].copy()
        fund_df["ReturnValue"] = fund_df["ReturnValue"].round(3)
        
        bench_df = df[df["VehicleID"] == "BENCHA"].copy()
        bench_df["ReturnValue"] = bench_df["ReturnValue"].round(3)

        # Define periods
        period_map = {
            "1 Month": DateOffset(months=1),
            "3 Month": DateOffset(months=3),
            "6 Month": DateOffset(months=6),
            "12 Month": DateOffset(months=12)
        }

        as_of_date = pd.to_datetime(as_of_date)

        records = []

        for label, offset in period_map.items():
            start_date = as_of_date - offset

            fund_ret = ExcelService.compounded_return(fund_df, start_date, as_of_date)
            bench_ret = ExcelService.compounded_return(bench_df, start_date, as_of_date)
            alpha = fund_ret - bench_ret if fund_ret is not None and bench_ret is not None else None

            records.append([as_of_date, label, fund_ret, bench_ret, alpha])

        # Final Report
        result_df = pd.DataFrame(records, columns=["AsOf", "Period", "FundReturn", "BenchmarkReturn", "Alpha"])

        #result_df["FundReturn"] = result_df["FundReturn"].round(3)
        #result_df["BenchmarkReturn"] = result_df["BenchmarkReturn"].round(3)
        result_df["Alpha"] = result_df["Alpha"].round(3)

        return result_df.to_dict(orient="records")
