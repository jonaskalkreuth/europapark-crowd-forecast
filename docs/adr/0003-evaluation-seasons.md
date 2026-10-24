# Evaluation uses summer seasons 2019 and 2022 onward

Crowd levels exist back to 2014, but free school-holiday data does not. French holidays start in late 2017 and Swiss holidays only in December 2019. We start at summer 2019 and type in the 2019 Swiss school holidays by hand. We drop 2020 and 2021 because COVID closures and capacity caps distorted them.

Each test season is predicted from all earlier seasons: 2024 from 2019, 2022 and 2023, then 2025 from those plus 2024. Summer 2026 is the holdout season, opened once at the end.

## Considered Options

- **Start at 2018 with two years of Swiss holidays typed in**: rejected. It costs more manual work for one extra training season.
- **Start at 2018 without Swiss holidays**: rejected. It would leave the nearby Swiss cantons out of holiday pressure.

## Winter

Winter seasons train on 2019/20 and 2022/23, validate on 2023/24 and test on 2024/25, then 2025/26. Winter 2021/22 is left out because COVID rules still applied. Winter has no holdout season: winter 2026/27 ends too late, so summer 2026 is the project's single final check.
