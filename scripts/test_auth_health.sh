#!/bin/bash

# 🧪 Quick Authentication Validation Test
echo "🚀 Testing Pixel AI Creator Authentication..."
echo ""

# Test 1: API Health Check
echo "📡 Testing API health..."
API_RESPONSE=$(curl -s http://localhost:8002/)
if [[ $API_RESPONSE == *"Welcome to Pixel AI Creator"* ]]; then
    echo "✅ API is running"
else
    echo "❌ API not responding"
    exit 1
fi

# Test 2: Frontend Health Check  
echo "🌐 Testing Frontend health..."
FRONTEND_RESPONSE=$(curl -s http://localhost:3002/)
if [[ $FRONTEND_RESPONSE == *"Pixel AI Creator"* ]]; then
    echo "✅ Frontend is running"
else
    echo "❌ Frontend not responding"
    exit 1
fi

# Test 3: Registration API Test
echo "📝 Testing registration API..."
REG_RESPONSE=$(curl -s -X POST http://localhost:8002/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "autotest@example.com",
    "password": "AutoTest123!",
    "first_name": "Auto",
    "last_name": "Test"
  }')

if [[ $REG_RESPONSE == *"User registered successfully"* ]] || [[ $REG_RESPONSE == *"Email already registered"* ]]; then
    echo "✅ Registration API working"
else
    echo "❌ Registration API failed: $REG_RESPONSE"
    exit 1
fi

# Test 4: Login API Test
echo "🔐 Testing login API..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8002/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@pixelai.com",
    "password": "Demo123!"
  }')

if [[ $LOGIN_RESPONSE == *"access_token"* ]]; then
    echo "✅ Login API working"
else
    echo "❌ Login API failed: $LOGIN_RESPONSE"
    exit 1
fi

echo ""
echo "🎉 All authentication tests passed!"
echo ""
echo "📋 Ready for manual testing:"
echo "   Frontend: http://localhost:3002"
echo "   Test Account: demo@pixelai.com / Demo123!"
echo "   Test Account: testuser@example.com / password123"
echo ""
echo "📖 See MANUAL_TESTING_GUIDE.md for complete testing instructions"