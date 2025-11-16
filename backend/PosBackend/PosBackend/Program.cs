
using Microsoft.EntityFrameworkCore;
using System.Collections.Generic;

var builder = WebApplication.CreateBuilder(args);

// Configure EF Core with SQL Server
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection")
    ?? "Server=localhost;Database=MyAppDb;User Id=sa;Password=YourStrongPassword;";
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(connectionString));

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
        policy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader());
});

var app = builder.Build();
app.UseCors("AllowAll");


// -------------------- ENDPOINTS --------------------

// Products
app.MapGet("/api/products", async (AppDbContext db) =>
    await db.Products.Where(p => p.IsActive).ToListAsync());

app.MapGet("/api/products/{id}", async (AppDbContext db, int id) =>
    await db.Products.FindAsync(id) is Product p ? Results.Ok(p) : Results.NotFound());

app.MapPost("/api/products", async (AppDbContext db, Product product) =>
{
    product.CreatedAt = DateTime.UtcNow;
    product.UpdatedAt = DateTime.UtcNow;
    db.Products.Add(product);
    await db.SaveChangesAsync();
    return Results.Created($"/api/products/{product.Id}", product);
});

app.MapPut("/api/products/{id}", async (AppDbContext db, int id, Product update) =>
{
    var product = await db.Products.FindAsync(id);
    if (product is null) return Results.NotFound();
    product.Name = update.Name ?? product.Name;
    product.Description = update.Description ?? product.Description;
    product.Price = update.Price != 0 ? update.Price : product.Price;
    product.Stock = update.Stock != 0 ? update.Stock : product.Stock;
    product.Category = update.Category ?? product.Category;
    product.Image = update.Image ?? product.Image;
    product.IsActive = update.IsActive;
    product.UpdatedAt = DateTime.UtcNow;
    await db.SaveChangesAsync();
    return Results.Ok(product);
});

app.MapDelete("/api/products/{id}", async (AppDbContext db, int id) =>
{
    var product = await db.Products.FindAsync(id);
    if (product is null) return Results.NotFound();
    product.IsActive = false;
    product.UpdatedAt = DateTime.UtcNow;
    await db.SaveChangesAsync();
    return Results.Ok(new { message = "Product deleted successfully" });
});

// Transactions
app.MapGet("/api/transactions", async (AppDbContext db) =>
    await db.Transactions.Include(t => t.Items).OrderByDescending(t => t.CreatedAt).ToListAsync());

app.MapGet("/api/transactions/{id}", async (AppDbContext db, int id) =>
    await db.Transactions.Include(t => t.Items).FirstOrDefaultAsync(t => t.Id == id) is Transaction txn ? Results.Ok(txn) : Results.NotFound());

app.MapPost("/api/transactions", async (AppDbContext db, Transaction transaction) =>
{
    int count = await db.Transactions.CountAsync();
    transaction.TransactionNumber = $"TXN-{count + 1:000000}";
    transaction.CreatedAt = DateTime.UtcNow;
    transaction.Status = "completed";

    foreach (var item in transaction.Items)
    {
        var product = await db.Products.FindAsync(item.ProductId);
        if (product != null)
        {
            product.Stock -= item.Quantity;
            product.UpdatedAt = DateTime.UtcNow;
        }
    }

    db.Transactions.Add(transaction);
    await db.SaveChangesAsync();
    return Results.Created($"/api/transactions/{transaction.Id}", transaction);
});

// Categories
app.MapGet("/api/categories", async (AppDbContext db) =>
{
    var categories = await db.Products.Where(p => p.IsActive).Select(p => p.Category).Distinct().ToListAsync();
    return Results.Ok(new { categories });
});

// Dashboard Stats
app.MapGet("/api/dashboard/stats", async (AppDbContext db) =>
{
    var totalProducts = await db.Products.CountAsync(p => p.IsActive);
    var totalTransactions = await db.Transactions.CountAsync();
    var todayStart = DateTime.UtcNow.Date;
    var todaySales = await db.Transactions.Where(t => t.CreatedAt >= todayStart).ToListAsync();
    var todayRevenue = todaySales.Sum(t => t.Total);
    var todayTransactions = todaySales.Count;
    var lowStockCount = await db.Products.CountAsync(p => p.Stock < 10 && p.IsActive);

    return Results.Ok(new
    {
        totalProducts,
        totalTransactions,
        todayRevenue,
        todayTransactions,
        lowStockCount
    });
});

app.Run();


// -------------------- MODELS --------------------
public class Product
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public string Description { get; set; } = "";
    public double Price { get; set; }
    public int Stock { get; set; }
    public string Category { get; set; } = "General";
    public string? Image { get; set; }
    public bool IsActive { get; set; } = true;
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;
}

public class Transaction
{
    public int Id { get; set; }
    public string TransactionNumber { get; set; } = "";
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public string Status { get; set; } = "completed";
    public double Subtotal { get; set; }
    public double Tax { get; set; }
    public double Discount { get; set; }
    public double Total { get; set; }
    public string PaymentMethod { get; set; } = "cash";
    public string? CustomerName { get; set; }
    public string? Notes { get; set; }
    public List<TransactionItem> Items { get; set; } = new();
}

public class TransactionItem
{
    public int Id { get; set; }
    public int TransactionId { get; set; }
    public Transaction Transaction { get; set; } = null!;
    public int ProductId { get; set; }
    public string ProductName { get; set; } = "";
    public double Price { get; set; }
    public int Quantity { get; set; }
    public double Total { get; set; }
}

// -------------------- DB CONTEXT --------------------
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
    public DbSet<Product> Products => Set<Product>();
    public DbSet<Transaction> Transactions => Set<Transaction>();
    public DbSet<TransactionItem> TransactionItems => Set<TransactionItem>();
}