# api/dataAnalytics.py
from fastapi import APIRouter, Query
import pandas as pd
from fastapi import APIRouter, HTTPException
from services.excelServices import ExcelService
import numpy as np

router = APIRouter()

@router.get("/reportReturns", summary="Get report for the Returns Excel file")
async def reportReturns(as_of_date: str | None = Query(
                             default="2025-06-30",
                             description="as_of_date parameter. Example: 2025-06-30"
                             )):
    try:
        returns_df = ExcelService.read_excel("Returns.xlsx")
        report = ExcelService.generate_returns(returns_df, as_of_date)
        return {"report": report}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/reportExposure", summary="Get report for the Constituent_Data Excel file")
async def reportExposure(start_date: str | None = Query(
                             default="2025-04-01",
                             description="end_date parameter. Example: 2025-04-01"
                             ),
                         end_date: str | None = Query(
                             default="2025-06-30",
                             description="end_date parameter. Example: 2025-06-30"
                             ),
                         group_by_cols: str | None = Query(
                             default="AntipodesRegion",
                             description="Grouping function parameter. Valid Options: SecurityName,LocalCurrency,CountryCode,AntipodesRegion,IndustryName,SubIndustryName"
                             )):
    try:
        start_date = pd.Timestamp(start_date)

        end_date = pd.Timestamp(end_date)

        # Check date logic
        if start_date > end_date:
            raise HTTPException(400, "start_date cannot be greater than end_date")
        
        group_by_col_list = []
        if group_by_cols:
            group_by_col_list = [x for x in group_by_cols.split(",")]

        constituent_df = ExcelService.read_excel("Constituent_Data.xlsx")

        # Check date logic
        if not all(col in constituent_df.columns for col in group_by_col_list):
            raise HTTPException(400, "Invalid group by columns list.")
        group_by_col_list.append("IndexID")

        # Converting IndexDate to datetime
        constituent_df["IndexDate"] = pd.to_datetime(constituent_df["IndexDate"])
        
        # Separate start & end date report snapshot
        start_df = (
            constituent_df[constituent_df["IndexDate"] == start_date]
            .groupby(group_by_col_list, as_index=False)["Weight"]
            .sum()
            .rename(columns={"Weight": "StartWeight"})
        )

        end_df = (
            constituent_df[constituent_df["IndexDate"] == end_date]
            .groupby(group_by_col_list, as_index=False)["Weight"]
            .sum()
            .rename(columns={"Weight": "EndWeight"})
        )

        # Merge & compute difference
        report_df = pd.merge(start_df, end_df, on=group_by_col_list, how="outer").fillna(0)
        report_df["Difference"] = (report_df["StartWeight"] - report_df["EndWeight"]).round(2)

        report_df["StartWeight"] = report_df["StartWeight"].round(2)
        report_df["EndWeight"] = report_df["EndWeight"].round(2)

        report_df = report_df.rename(columns={
            "IndexID": "VehicleID"
        })
        
        report_df.insert(0, "StartDate", start_date.date())
        report_df.insert(1, "EndDate", end_date.date())

        return report_df.to_dict(orient="records")
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
