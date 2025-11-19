#!/bin/bash

# Watcher Protocol Monitoring Script
# Checks system health and sends alerts if issues detected

set -e

API_URL="${API_URL:-http://localhost:8000}"
ALERT_EMAIL="${ALERT_EMAIL:-admin@example.com}"
SLACK_WEBHOOK="${SLACK_WEBHOOK:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if service is healthy
check_health() {
    local service=$1
    local url=$2

    echo -n "Checking $service... "

    if curl -f -s -o /dev/null "$url"; then
        echo -e "${GREEN}OK${NC}"
        return 0
    else
        echo -e "${RED}FAILED${NC}"
        return 1
    fi
}

# Check scraper status
check_scrapers() {
    echo "Checking scrapers..."

    response=$(curl -s "$API_URL/api/v1/admin/scrapers/status")

    if echo "$response" | grep -q "failed"; then
        echo -e "${YELLOW}Warning: Some scrapers have failures${NC}"
        return 1
    fi

    echo -e "${GREEN}All scrapers OK${NC}"
    return 0
}

# Check database connectivity
check_database() {
    echo "Checking database..."

    if docker-compose exec -T postgres pg_isready -U watcher > /dev/null 2>&1; then
        echo -e "${GREEN}Database OK${NC}"
        return 0
    else
        echo -e "${RED}Database connection failed${NC}"
        return 1
    fi
}

# Check disk space
check_disk() {
    echo "Checking disk space..."

    usage=$(df -h / | tail -1 | awk '{print $5}' | sed 's/%//')

    if [ "$usage" -gt 90 ]; then
        echo -e "${RED}Disk usage critical: ${usage}%${NC}"
        return 1
    elif [ "$usage" -gt 75 ]; then
        echo -e "${YELLOW}Disk usage warning: ${usage}%${NC}"
        return 1
    else
        echo -e "${GREEN}Disk usage OK: ${usage}%${NC}"
        return 0
    fi
}

# Send alert
send_alert() {
    local message=$1

    echo "Sending alert: $message"

    # Send email if configured
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "Watcher Protocol Alert" "$ALERT_EMAIL" || true
    fi

    # Send Slack notification if configured
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🦇 Watcher Protocol Alert: $message\"}" \
            "$SLACK_WEBHOOK" || true
    fi
}

# Main monitoring logic
main() {
    echo "=== Watcher Protocol Health Check ==="
    echo "Time: $(date)"
    echo ""

    failed=0

    # Check API health
    check_health "API" "$API_URL/health" || failed=1

    # Check database
    check_database || failed=1

    # Check Redis
    check_health "Redis" "http://localhost:6379" || failed=1

    # Check scrapers
    check_scrapers || failed=1

    # Check disk space
    check_disk || failed=1

    echo ""

    if [ $failed -eq 1 ]; then
        echo -e "${RED}Health check FAILED${NC}"
        send_alert "Health check failed. Please investigate."
        exit 1
    else
        echo -e "${GREEN}All checks PASSED${NC}"
        exit 0
    fi
}

# Run main function
main "$@"
