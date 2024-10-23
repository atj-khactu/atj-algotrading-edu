//+------------------------------------------------------------------+
//|                                               PA_Recognition.mq5 |
//|                              Khac Tu Nguyen - ATJ Traders s.r.o. |
//|                                     https://www.atj-traders.com/ |
//+------------------------------------------------------------------+
#property copyright "Khac Tu Nguyen - ATJ Traders s.r.o."
#property link      "https://www.atj-traders.com/"
#property version   "1.00"

input int number_of_candles = 20;

//+------------------------------------------------------------------+
//| Create the horizontal line                                       |
//+------------------------------------------------------------------+
bool HLineCreate(const long            chart_ID=0,        // chart's ID
                 const string          name="HLine",      // line name
                 const int             sub_window=0,      // subwindow index
                 double                price=0,           // line price
                 const color           clr=clrRed,        // line color
                 const ENUM_LINE_STYLE style=STYLE_SOLID, // line style
                 const int             width=1,           // line width
                 const bool            back=false,        // in the background
                 const bool            selection=true,    // highlight to move
                 const bool            hidden=true,       // hidden in the object list
                 const long            z_order=0)         // priority for mouse click
  {
//--- if the price is not set, set it at the current Bid price level
   if(!price)
      price=SymbolInfoDouble(Symbol(),SYMBOL_BID);
//--- reset the error value
   ResetLastError();
//--- create a horizontal line
   if(!ObjectCreate(chart_ID,name,OBJ_HLINE,sub_window,0,price))
     {
      Print(__FUNCTION__,
            ": failed to create a horizontal line! Error code = ",GetLastError());
      return(false);
     }
//--- set line color
   ObjectSetInteger(chart_ID,name,OBJPROP_COLOR,clr);
//--- set line display style
   ObjectSetInteger(chart_ID,name,OBJPROP_STYLE,style);
//--- set line width
   ObjectSetInteger(chart_ID,name,OBJPROP_WIDTH,width);
//--- display in the foreground (false) or background (true)
   ObjectSetInteger(chart_ID,name,OBJPROP_BACK,back);
//--- enable (true) or disable (false) the mode of moving the line by mouse
//--- when creating a graphical object using ObjectCreate function, the object cannot be
//--- highlighted and moved by default. Inside this method, selection parameter
//--- is true by default making it possible to highlight and move the object
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTABLE,selection);
   ObjectSetInteger(chart_ID,name,OBJPROP_SELECTED,selection);
//--- hide (true) or display (false) graphical object name in the object list
   ObjectSetInteger(chart_ID,name,OBJPROP_HIDDEN,hidden);
//--- set the priority for receiving the event of a mouse click in the chart
   ObjectSetInteger(chart_ID,name,OBJPROP_ZORDER,z_order);
//--- successful execution
   return(true);
  }
  
  
 string GetRatesCSV(int num_candles=1)
 {
   string csv_data;

   MqlRates rates[];
   ArraySetAsSeries(rates,true);
   int copied=CopyRates(Symbol(),Period(),1,num_candles,rates);
      
      int size=fmin(copied,10);
      for(int i=0;i<size;i++)
        {
        string time = TimeToString(rates[i].time);
        string open = DoubleToString(rates[i].open);
        string high = DoubleToString(rates[i].high);
        string low = DoubleToString(rates[i].low);
        string close = DoubleToString(rates[i].close);
        
        string data_str = time + "," + open + "," + high + "," + low + "," + close + "\n";
        csv_data = csv_data + data_str;
        }
        
   return(csv_data);
 }
 
string SendDataToPythonServer(string csv_data)
{
//---
   
   string cookie=NULL,headers;
   char post[], result[];
   string url="http://127.0.0.1:5005/";
//--- Resetting the last error code
   ResetLastError();
//---
   StringToCharArray(csv_data, post);
   
   int res=WebRequest("GET",url,cookie,NULL,500,post,0,result,headers);
   
   string request_result = CharArrayToString(result);
   return(request_result);

}
  
  
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
//--- create timer
   EventSetTimer(5);
   
//---
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
//--- destroy timer
   EventKillTimer();
   
  }

//+------------------------------------------------------------------+
//| Timer function                                                   |
//+------------------------------------------------------------------+
void OnTimer()
  {
//---
  string candle_data_csv = GetRatesCSV(number_of_candles);
  string pa_analysis = SendDataToPythonServer(candle_data_csv);
  
  string sr_values[];
  string sep = ",";
  ushort u_sep;
  u_sep=StringGetCharacter(sep,0);
  StringSplit(pa_analysis, u_sep, sr_values);
  
  Print(sr_values[0]);
  Print(sr_values[1]);
  
  double resistance = StringToDouble(sr_values[0]);
  double support = StringToDouble(sr_values[1]);
  
  Print(resistance, support);
  
  bool obj_res1;
   bool obj_res2;
   
   obj_res1 = HLineCreate(0, "Line 1", 0, resistance);
   obj_res2 = HLineCreate(0, "Line 2", 0, support);
   
   Print(TimeToString(TimeCurrent()));
   Print("OBJ1 Create Result: " + obj_res1);
   Print("OBJ2 Create Result: " + obj_res2);
  }
//+------------------------------------------------------------------+
