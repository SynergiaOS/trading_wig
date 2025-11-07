#!/usr/bin/env python3
"""
WIG80 QuestDB Management Script
Handles common database maintenance operations
"""

import asyncio
import aiohttp
import logging
import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuestDBManager:
    """QuestDB management operations"""
    
    def __init__(self, host: str = "localhost", port: int = 8812, auth: tuple = ("admin", "quest")):
        self.base_url = f"http://{host}:{port}"
        self.auth = auth
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(auth=aiohttp.BasicAuth(*self.auth))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def health_check(self) -> bool:
        """Check if QuestDB is healthy"""
        try:
            async with self.session.get(f"{self.base_url}/health") as response:
                return response.status == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
            
    async def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Execute SQL query via REST API"""
        try:
            async with self.session.get(f"{self.base_url}/exec", params={"query": query}) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("dataset", [])
                else:
                    logger.error(f"Query failed with status {response.status}")
                    return []
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return []
            
    async def get_table_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        query = """
        SELECT table, rows, allocated_bytes, used_bytes, disk_size_bytes
        FROM information_schema.tables
        WHERE table IN ('wig80_historical', 'ai_insights', 'market_correlations', 'valuation_analysis')
        """
        return await self.execute_query(query)
        
    async def get_table_size_stats(self) -> List[Dict[str, Any]]:
        """Get detailed table size statistics"""
        stats = []
        tables = ['wig80_historical', 'ai_insights', 'market_correlations', 'valuation_analysis']
        
        for table in tables:
            query = f"""
            SELECT 
                '{table}' as table_name,
                COUNT(*) as row_count,
                MIN(ts) as earliest_timestamp,
                MAX(ts) as latest_timestamp,
                COUNT(DISTINCT symbol) as symbol_count
            FROM {table}
            """
            result = await self.execute_query(query)
            if result:
                stats.append(result[0])
                
        return stats
        
    async def optimize_tables(self, tables: List[str] = None) -> bool:
        """Optimize database tables"""
        if tables is None:
            tables = ['wig80_historical', 'ai_insights', 'market_correlations', 'valuation_analysis']
            
        success = True
        for table in tables:
            try:
                query = f"OPTIMIZE TABLE {table};"
                result = await self.execute_query(query)
                logger.info(f"Optimized table {table}")
            except Exception as e:
                logger.error(f"Failed to optimize table {table}: {e}")
                success = False
                
        return success
        
    async def vacuum_tables(self, tables: List[str] = None) -> bool:
        """Vacuum database tables"""
        if tables is None:
            tables = ['wig80_historical', 'ai_insights', 'market_correlations', 'valuation_analysis']
            
        success = True
        for table in tables:
            try:
                query = f"VACUUM TABLE {table};"
                result = await self.execute_query(query)
                logger.info(f"Vacuumed table {table}")
            except Exception as e:
                logger.error(f"Failed to vacuum table {table}: {e}")
                success = False
                
        return success
        
    async def clean_old_data(self, days_to_keep: int = 30) -> bool:
        """Clean old data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.strftime("%Y-%m-%d %H:%M:%S")
        
        tables = ['wig80_historical', 'ai_insights', 'market_correlations', 'valuation_analysis']
        success = True
        
        for table in tables:
            try:
                query = f"DELETE FROM {table} WHERE ts < '{cutoff_str}';"
                result = await self.execute_query(query)
                logger.info(f"Cleaned old data from {table} (before {cutoff_str})")
            except Exception as e:
                logger.error(f"Failed to clean data from {table}: {e}")
                success = False
                
        return success
        
    async def create_backup_directory(self, backup_dir: str = None) -> str:
        """Create backup directory with timestamp"""
        if backup_dir is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backup_questdb_{timestamp}"
            
        os.makedirs(backup_dir, exist_ok=True)
        logger.info(f"Created backup directory: {backup_dir}")
        return backup_dir
        
    async def export_table_data(self, table: str, backup_dir: str, limit: int = None) -> bool:
        """Export table data to JSON file"""
        try:
            if limit:
                query = f"SELECT * FROM {table} LIMIT {limit};"
            else:
                query = f"SELECT * FROM {table};"
                
            data = await self.execute_query(query)
            
            backup_file = os.path.join(backup_dir, f"{table}.json")
            with open(backup_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                
            logger.info(f"Exported {len(data)} rows from {table} to {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to export {table}: {e}")
            return False
            
    async def backup_database(self, backup_dir: str = None, export_all: bool = True) -> bool:
        """Create database backup"""
        backup_dir = await self.create_backup_directory(backup_dir)
        
        try:
            # Export table schemas
            tables = ['wig80_historical', 'ai_insights', 'market_correlations', 'valuation_analysis']
            
            for table in tables:
                if export_all:
                    await self.export_table_data(table, backup_dir)
                else:
                    await self.export_table_data(table, backup_dir, limit=1000)  # Sample data only
                    
            # Export metadata
            stats = await self.get_table_stats()
            stats_file = os.path.join(backup_dir, "database_stats.json")
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
                
            logger.info(f"Database backup completed: {backup_dir}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False
            
    async def get_query_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get query performance log"""
        query = f"""
        SELECT query, count, avg_time_ms, max_time_ms, last_execution
        FROM information_schema.query_log
        ORDER BY count DESC
        LIMIT {limit}
        """
        return await self.execute_query(query)
        
    async def get_long_running_queries(self) -> List[Dict[str, Any]]:
        """Get currently running queries"""
        query = """
        SELECT query_id, query, start_time, execution_time_ms, user
        FROM information_schema.queries
        WHERE status = 'running'
        ORDER BY start_time DESC
        """
        return await self.execute_query(query)
        
    async def kill_query(self, query_id: str) -> bool:
        """Kill a running query"""
        try:
            query = f"KILL QUERY {query_id};"
            await self.execute_query(query)
            logger.info(f"Killed query {query_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to kill query {query_id}: {e}")
            return False
            
    async def show_running_queries(self) -> List[Dict[str, Any]]:
        """Show currently running queries"""
        queries = await self.get_long_running_queries()
        if queries:
            logger.info("Currently running queries:")
            for q in queries:
                logger.info(f"  Query ID: {q[0]}, User: {q[4]}, Start: {q[2]}")
        else:
            logger.info("No running queries")
        return queries
        
    async def monitor_performance(self) -> Dict[str, Any]:
        """Monitor database performance"""
        try:
            stats = await self.get_table_stats()
            queries = await self.get_query_log(10)
            
            # Check for slow queries
            slow_queries = [q for q in queries if q[2] > 5000]  # > 5 seconds
            
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'table_stats': stats,
                'slow_queries_count': len(slow_queries),
                'slow_queries': slow_queries,
                'total_queries_24h': sum(q[1] for q in queries if q[4] >= datetime.now() - timedelta(hours=24))
            }
            
            return performance_data
        except Exception as e:
            logger.error(f"Performance monitoring failed: {e}")
            return {}

async def health_check_action(manager: QuestDBManager):
    """Health check action"""
    logger.info("Performing health check...")
    
    if await manager.health_check():
        logger.info("✅ QuestDB is healthy and responding")
        
        # Get basic stats
        stats = await manager.get_table_size_stats()
        logger.info("\n📊 Database Statistics:")
        for stat in stats:
            logger.info(f"  {stat['table_name']}: {stat['row_count']:,} rows, "
                       f"{stat['symbol_count']} symbols, "
                       f"from {stat['earliest_timestamp']} to {stat['latest_timestamp']}")
    else:
        logger.error("❌ QuestDB is not responding")
        sys.exit(1)

async def backup_action(manager: QuestDBManager, args):
    """Backup action"""
    logger.info(f"Creating database backup...")
    
    success = await manager.backup_database(
        backup_dir=args.directory,
        export_all=args.full
    )
    
    if success:
        logger.info("✅ Backup completed successfully")
    else:
        logger.error("❌ Backup failed")
        sys.exit(1)

async def optimize_action(manager: QuestDBManager, args):
    """Optimize action"""
    logger.info("Optimizing database tables...")
    
    success = await manager.optimize_tables()
    
    if success:
        logger.info("✅ Optimization completed")
    else:
        logger.error("❌ Optimization failed")

async def clean_action(manager: QuestDBManager, args):
    """Clean action"""
    logger.info(f"Cleaning data older than {args.days} days...")
    
    success = await manager.clean_old_data(args.days)
    
    if success:
        logger.info("✅ Data cleaning completed")
    else:
        logger.error("❌ Data cleaning failed")

async def monitor_action(manager: QuestDBManager, args):
    """Monitor action"""
    logger.info("Monitoring database performance...")
    
    if args.continuous:
        logger.info("Continuous monitoring (Ctrl+C to stop)")
        while True:
            performance = await manager.monitor_performance()
            if performance:
                logger.info(f"📈 Performance: {performance['slow_queries_count']} slow queries, "
                           f"{performance['total_queries_24h']} queries in 24h")
            await asyncio.sleep(args.interval)
    else:
        performance = await manager.monitor_performance()
        logger.info(f"Performance data: {json.dumps(performance, indent=2)}")

async def query_action(manager: QuestDBManager, args):
    """Execute custom query"""
    try:
        with open(args.file, 'r') as f:
            query = f.read()
    except Exception as e:
        logger.error(f"Failed to read query file: {e}")
        sys.exit(1)
        
    logger.info(f"Executing query from {args.file}...")
    results = await manager.execute_query(query)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {args.output}")
    else:
        logger.info(f"Query returned {len(results)} rows")
        for row in results[:10]:  # Show first 10 rows
            logger.info(row)
        if len(results) > 10:
            logger.info(f"... and {len(results) - 10} more rows")

async def show_queries_action(manager: QuestDBManager, args):
    """Show running queries"""
    await manager.show_running_queries()

async def kill_query_action(manager: QuestDBManager, args):
    """Kill query action"""
    logger.info(f"Killing query {args.query_id}...")
    success = await manager.kill_query(args.query_id)
    
    if success:
        logger.info("✅ Query killed successfully")
    else:
        logger.error("❌ Failed to kill query")
        sys.exit(1)

def create_parser():
    """Create command line parser"""
    parser = argparse.ArgumentParser(description="WIG80 QuestDB Management Tool")
    parser.add_argument("--host", default="localhost", help="QuestDB host")
    parser.add_argument("--port", default=8812, type=int, help="QuestDB port")
    parser.add_argument("--user", default="admin", help="QuestDB username")
    parser.add_argument("--password", default="quest", help="QuestDB password")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Health check
    health_parser = subparsers.add_parser("health", help="Health check")
    
    # Backup
    backup_parser = subparsers.add_parser("backup", help="Backup database")
    backup_parser.add_argument("--directory", help="Backup directory")
    backup_parser.add_argument("--full", action="store_true", help="Full backup (all data)")
    
    # Optimize
    optimize_parser = subparsers.add_parser("optimize", help="Optimize tables")
    
    # Clean
    clean_parser = subparsers.add_parser("clean", help="Clean old data")
    clean_parser.add_argument("--days", type=int, default=30, help="Days of data to keep")
    
    # Monitor
    monitor_parser = subparsers.add_parser("monitor", help="Monitor performance")
    monitor_parser.add_argument("--continuous", action="store_true", help="Continuous monitoring")
    monitor_parser.add_argument("--interval", type=int, default=60, help="Monitoring interval (seconds)")
    
    # Query
    query_parser = subparsers.add_parser("query", help="Execute custom query")
    query_parser.add_argument("--file", required=True, help="SQL file to execute")
    query_parser.add_argument("--output", help="Output file for results")
    
    # Show queries
    show_parser = subparsers.add_parser("show-queries", help="Show running queries")
    
    # Kill query
    kill_parser = subparsers.add_parser("kill-query", help="Kill running query")
    kill_parser.add_argument("--query-id", required=True, help="Query ID to kill")
    
    return parser

async def main():
    """Main function"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
        
    # Create manager
    auth = (args.user, args.password)
    manager = QuestDBManager(args.host, args.port, auth)
    
    # Execute action
    async with manager:
        if args.command == "health":
            await health_check_action(manager)
        elif args.command == "backup":
            await backup_action(manager, args)
        elif args.command == "optimize":
            await optimize_action(manager, args)
        elif args.command == "clean":
            await clean_action(manager, args)
        elif args.command == "monitor":
            await monitor_action(manager, args)
        elif args.command == "query":
            await query_action(manager, args)
        elif args.command == "show-queries":
            await show_queries_action(manager, args)
        elif args.command == "kill-query":
            await kill_query_action(manager, args)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
