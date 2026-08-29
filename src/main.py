from .postgres_loader import load_to_postgres


def main():
    print("Starting e-commerce data pipeline...\n")

    row_counts = load_to_postgres()

    print("\nPipeline completed successfully.")
    print("Loaded tables:")
    for table_name, row_count in row_counts.items():
        print(f"  - {table_name}: {row_count} rows")


if __name__ == "__main__":
    main()