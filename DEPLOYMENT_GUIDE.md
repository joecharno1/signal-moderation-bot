# 🚀 Railway Deployment Guide - Signal Moderation Bot

## ✅ **What You're Deploying**

A complete Signal moderation bot solution with:
- 🤖 **Signal API Server** (signal-cli-rest-api)
- 🌐 **Web Dashboard** (Flask application)
- 📊 **Member Management** for 500+ member groups
- 🔧 **Moderation Tools** and automation
- 📱 **Mobile-responsive interface**

## 🎯 **Step-by-Step Deployment**

### **Step 1: Prepare Railway Account**
1. Go to [railway.app](https://railway.app)
2. Click "Login" → "Login with GitHub"
3. Authorize Railway access
4. Add payment method for Hobby plan ($5/month recommended)

### **Step 2: Create Project**
1. Click "New Project" in Railway dashboard
2. Choose "Empty Project"
3. Name it "signal-moderation-bot"

### **Step 3: Deploy Your Code**

**Option A: GitHub Repository (Recommended)**
1. Create new GitHub repository
2. Upload all files from this folder
3. In Railway: "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Dockerfile and deploys

**Option B: Upload ZIP**
1. Zip this entire folder
2. In Railway: "Deploy from GitHub repo" → "Upload folder"
3. Select your ZIP file
4. Railway builds and deploys automatically

**Option C: Railway CLI**
```bash
# Install CLI
npm install -g @railway/cli

# Login and deploy
railway login
cd railway_moderation_bot
railway up
```

### **Step 4: Monitor Deployment**
1. Watch build logs in Railway dashboard
2. Wait for "Deployment successful" message
3. Note your Railway URL (e.g., `https://signal-moderation-bot-production.railway.app`)

### **Step 5: Verify Deployment**

**Test these endpoints:**
```bash
# Health check
curl https://your-app.railway.app/health

# Dashboard (should load web interface)
https://your-app.railway.app/

# API endpoints
curl https://your-app.railway.app/api/stats
```

### **Step 6: Add Bot to Your Group**
1. Open Signal on your phone
2. Add your bot account (+15614121835) to your 500-member group
3. Grant admin permissions if needed
4. Bot automatically detects and syncs members

## 🔧 **Configuration**

### **No Configuration Needed!**
Everything is pre-configured:
- ✅ Signal account already registered
- ✅ Database with existing profile data
- ✅ Web interface ready to use
- ✅ All API endpoints configured
- ✅ Health checks enabled

### **Environment Variables (Auto-set)**
- `PORT=5000` - Web interface port
- `SIGNAL_API_PORT=8080` - Signal API port

## 📊 **Testing Your Deployment**

### **1. Dashboard Test**
- Visit your Railway URL
- Should see "System Online & Healthy"
- Statistics should load (may show 0 initially)

### **2. API Test**
```bash
# Check health
curl https://your-app.railway.app/health

# Should return:
{
  "status": "healthy",
  "signal_api": true,
  "database": true
}
```

### **3. Group Integration Test**
1. Add bot to your Signal group
2. Refresh dashboard
3. Should see member count update
4. Try "Send Member List" button

## 🎯 **Success Indicators**

Your deployment is successful when:
- ✅ Railway shows "Deployment successful"
- ✅ Dashboard loads with green "System Online & Healthy"
- ✅ `/health` endpoint returns healthy status
- ✅ Member count shows your group size
- ✅ "Send Member List" works in dashboard

## 🔄 **Updates and Maintenance**

### **Automatic Updates**
- Push changes to GitHub
- Railway automatically redeploys
- Zero downtime deployments

### **Manual Updates**
```bash
# Using Railway CLI
railway up

# Or upload new ZIP via web interface
```

### **Monitoring**
- Railway dashboard shows logs and metrics
- Health checks run every 30 seconds
- Auto-restart on failures

## 💰 **Pricing Breakdown**

### **Railway Costs**
- **Free Tier**: 500 hours/month
  - Good for testing and small groups
  - May sleep after inactivity
- **Hobby Plan**: $5/month unlimited
  - Always-on hosting
  - Perfect for production use
  - Recommended for 500-member groups

### **Resource Usage**
- **Memory**: ~200MB (well within limits)
- **CPU**: Low usage, spikes during sync
- **Storage**: ~50MB for signal-cli data
- **Bandwidth**: Minimal for typical usage

## 🆘 **Troubleshooting**

### **Build Fails**
- Check Railway logs for specific errors
- Ensure all files uploaded correctly
- Verify Dockerfile syntax

### **Service Won't Start**
- Check if signal-cli data is included
- Verify file permissions
- Look for port conflicts in logs

### **Dashboard Loads But No Data**
- Bot may not be added to group yet
- Check Signal API connectivity
- Try force refresh in dashboard

### **Messages Not Sending**
- Verify bot has group permissions
- Check if account is still registered
- Test with health check endpoint

### **Database Issues**
- Ensure signal-cli-data folder is complete
- Check SQLite file permissions
- Verify account.db file exists

## 🔧 **Advanced Configuration**

### **Custom Domain (Optional)**
1. In Railway dashboard, go to Settings
2. Add custom domain
3. Configure DNS records
4. SSL automatically provisioned

### **Environment Variables**
Add in Railway dashboard if needed:
- `DEBUG=true` - Enable debug logging
- `MAX_MEMBERS=1000` - Increase member limit
- `SYNC_INTERVAL=300` - Profile sync interval (seconds)

### **Scaling**
For very large groups (1000+ members):
1. Upgrade to Railway Pro plan
2. Increase memory allocation
3. Consider database optimization

## 🎉 **Post-Deployment Checklist**

- [ ] Railway deployment successful
- [ ] Dashboard loads and shows healthy status
- [ ] Bot added to Signal group
- [ ] Member count appears correctly
- [ ] Test message sending works
- [ ] Search functionality works
- [ ] Mobile interface responsive
- [ ] Health checks passing
- [ ] Activity log updating

## 🚀 **You're Ready!**

Your Signal moderation bot is now:
- ✅ **Deployed permanently** on Railway
- ✅ **Accessible worldwide** via your Railway URL
- ✅ **Monitoring your group** 24/7
- ✅ **Ready for 500+ members** with full features
- ✅ **Mobile-friendly** for moderation on the go

**Welcome to professional Signal group moderation! 🎯**

