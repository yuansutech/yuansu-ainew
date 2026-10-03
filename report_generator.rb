require 'json'
require 'date'
module Reporting
  class ReportGenerator
    attr_reader :records, :title
    def initialize(title, records = [])
      @title = title
      @records = records
      @generated_at = nil
    end
    def add_record(record)
      @records << record
      self
    end
    def filter_by_date(range)
      @records.select { |r| range.include?(r[:date]) }
    end
    def group_by_category
      @records.group_by { |r| r[:category] }
    end
    def total_amount
      @records.sum { |r| r[:amount] }
    end
    def average_amount
      return 0 if @records.empty?
      total_amount / @records.length
    end
    def top_records(count)
      @records.sort_by { |r| -r[:amount] }.first(count)
    end
    def generate
      @generated_at = DateTime.now
      {
        title: @title,
        generated_at: @generated_at.iso8601,
        total: total_amount,
        average: average_amount,
        categories: group_by_category.keys
      }
    end
    def to_json(*args)
      generate.to_json(*args)
    end
    def summary_line
      "#{@title}: #{@records.length} records, total #{total_amount}"
    end
  end
end
generator = Reporting::ReportGenerator.new("Q1 Report")
generator.add_record({ date: Date.new(2024, 1, 15), category: "sales", amount: 1200 })
generator.add_record({ date: Date.new(2024, 2, 20), category: "sales", amount: 800 })
generator.add_record({ date: Date.new(2024, 3, 10), category: "refund", amount: -200 })
puts generator.summary_line
puts generator.total_amount
puts generator.average_amount
top = generator.top_records(2)
top.each { |r| puts r[:amount] }
report = generator.generate
puts report[:title]
puts report[:generated_at]
missing = generator.records.find { |r| r[:category] == "unknown" }
puts missing[:amount]
puts generator.to_json
