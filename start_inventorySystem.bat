@echo off
:: Change directory to the web app's directory
cd "C:\Users\kenneths\Projects\pngumit_InvoiceInventory"
waitress-serve --call "main:create_app"