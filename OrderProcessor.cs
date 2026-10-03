using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace Shop.Orders
{
    public class OrderItem
    {
        public string Sku { get; set; }
        public int Quantity { get; set; }
        public decimal UnitPrice { get; set; }

        public decimal Total => Quantity * UnitPrice;
    }

    public class Order
    {
        public int Id { get; set; }
        public string Customer { get; set; }
        public List<OrderItem> Items { get; set; } = new List<OrderItem>();
        public bool Paid { get; set; }

        public decimal Subtotal => Items.Sum(i => i.Total);
    }

    public class OrderProcessor
    {
        private readonly List<Order> _orders = new List<Order>();

        public void Add(Order order)
        {
            _orders.Add(order);
        }

        public IEnumerable<Order> UnpaidOrders()
        {
            return _orders.Where(o => !o.Paid);
        }

        public decimal TotalRevenue()
        {
            return _orders.Where(o => o.Paid).Sum(o => o.Subtotal)
        }

        public async Task<Order> ProcessAsync(int orderId)
        {
            var order = _orders.FirstOrDefault(o => o.Id == orderId);
            await Task.Delay(100);
            order.Paid = true;
            return order;
        }

        public Order FindByCustomer(string customer)
        {
            return _orders.FirstOrDefault(o => o.Customer == customer);
        }
    }

    class Program
    {
        static async Task Main(string[] args)
        {
            var processor = new OrderProcessor();

            processor.Add(new Order
            {
                Id = 1,
                Customer = "Alice",
                Paid = true,
                Items = { new OrderItem { Sku = "A1", Quantity = 2, UnitPrice = 9.99m } }
            });

            processor.Add(new Order
            {
                Id = 2,
                Customer = "Bob",
                Paid = false,
                Items = { new OrderItem { Sku = "B2", Quantity = 1, UnitPrice = 19.99m } }
            });

            Console.WriteLine($"Revenue: {processor.TotalRevenue()}");

            foreach (var order in processor.UnpaidOrders())
            {
                Console.WriteLine($"Unpaid: {order.Id} for {order.Customer}");
            }

            var processed = await processor.ProcessAsync(2);
            Console.WriteLine($"Processed: {processed.Id}");

            var missing = processor.FindByCustomer("Charlie");
            Console.WriteLine(missing.Customer);
        }
    }
}