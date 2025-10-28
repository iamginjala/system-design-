from utils.logger import get_app_logger, get_request_logger, get_error_logger

print("Testing your logger...\n")

# Test 1: App Logger (should show DEBUG, INFO, WARNING, ERROR)
print("=== Testing App Logger ===")
app_logger = get_app_logger()
app_logger.debug("This is a DEBUG message - very detailed")
app_logger.info("This is an INFO message - normal operation")
app_logger.warning("This is a WARNING message - potential problem")
app_logger.error("This is an ERROR message - something failed")

# Test 2: Request Logger (should show INFO, WARNING, ERROR but NOT DEBUG)
print("\n=== Testing Request Logger ===")
req_logger = get_request_logger()
req_logger.debug("This DEBUG should NOT appear (level is INFO)")
req_logger.info("Request: GET /api/products | IP: 192.168.1.1")
req_logger.info("Response: 200 OK | Time: 45.2ms")

# Test 3: Error Logger (should show ONLY ERROR and CRITICAL)
print("\n=== Testing Error Logger ===")
err_logger = get_error_logger()
err_logger.info("This INFO should NOT appear (level is ERROR)")
err_logger.error("Database connection failed!")
err_logger.critical("Redis is down! Application cannot continue!")

print("\n✅ Test complete! Check the logs/ folder for log files.")