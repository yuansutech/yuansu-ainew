library(stats)
load_sales_data <- function(path) {
    data <- read.csv(path, stringsAsFactors = FALSE)
    data$date <- as.Date(data$date)
    data$revenue <- data$quantity * data$unit_price
    return(data)
}
summarize_sales <- function(data) {
    total <- sum(data$revenue)
    average <- mean(data$revenue)
    median_value <- median(data$revenue)
    list(
        total = total,
        average = average,
        median = median_value,
        count = nrow(data)
    )
}
top_products <- function(data, n = 5) {
    aggregated <- aggregate(revenue ~ product, data = data, FUN = sum)
    aggregated <- aggregated[order(-aggregated$revenue), ]
    return(head(aggregated, n))
}
filter_by_date <- function(data, start_date, end_date) {
    subset(data, date >= start_date & date <= end_date)
}
plot_trend <- function(data) {
    daily <- aggregate(revenue ~ date, data = data, FUN = sum)
    plot(daily$date, daily$revenue, type = "l", main = "Revenue Trend")
}
sales <- data.frame(
    date = as.Date(c("2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04")),
    product = c("A", "B", "A", "C"),
    quantity = c(10, 5, 8, 3),
    unit_price = c(9.99, 19.99, 9.99, 4.99)
)
sales$revenue <- sales$quantity * sales$unit_price
summary_stats <- summarize_sales(sales)
print(summary_stats$total)
print(summary_stats$average)
top <- top_products(sales, 2)
print(top)
january <- filter_by_date(sales, as.Date("2024-01-01"), as.Date("2024-01-31"))
print(nrow(january))
missing_product <- sales[sales$product == "Z", ]
print(missing_product$revenue[1])
empty_result <- filter_by_date(sales, as.Date("2025-01-01"), as.Date("2025-12-31"))
total_empty <- sum(empty_result$revenue)
print(total_empty)
print(sales$revenue[10])
cat("Analysis complete\n")
