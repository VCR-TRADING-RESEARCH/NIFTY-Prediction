## C1 Direct NSE Special-session Audit Method

The three unresolved member-session dates are HDFC EQ on 2019-10-27, 2020-02-01 and 2020-11-14. This bounded check requests each exact legacy NSE cash-market archive from both NSE archive hosts, parses the ZIP CSV, and filters exact symbol, EQ series and trade date.

It validates one and only one matching row, positive finite OHLC with LOW <= min(OPEN,CLOSE) <= max(OPEN,CLOSE) <= HIGH, and finite nonnegative volume. It retains only source URL, archive SHA-256, row count and validation flags. It does not publish raw prices or volume.

A missing file or HTTP 404 is not proof that the exchange did not trade; it is reported as unavailable. Legacy files may omit ISIN, in which case symbol/series/date matching is reported transparently. The daily check does not establish adjusted returns or unlock C2.
