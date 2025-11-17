# Railway Deployment Guide

This guide will help you deploy your soccerSim app to Railway with automatic deployment on GitHub push.

## Prerequisites

- GitHub account
- Railway account (sign up at https://railway.app - free tier available)
- Your soccerSim repo pushed to GitHub

## Files Added for Railway

The following files have been configured for Railway deployment:

1. **Procfile** - Tells Railway how to start your app
2. **railway.toml** - Railway-specific configuration
3. **requirements.txt** - Updated with `gunicorn` for production server
4. **app.py** - Modified to use Railway's PORT environment variable

## Deployment Steps

### Step 1: Push to GitHub

First, commit and push these new files to your GitHub repo:

```bash
git add Procfile railway.toml requirements.txt app.py RAILWAY_DEPLOYMENT.md
git commit -m "Add Railway deployment configuration"
git push origin main
```

### Step 2: Connect Railway to GitHub

1. Go to https://railway.app and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. If this is your first time, authorize Railway to access your GitHub account
5. Select your **soccerSim** repository from the list
6. Railway will automatically detect it's a Python/Flask app and start deploying

### Step 3: Wait for Deployment

- Railway will install dependencies and start your app
- You'll see build logs in real-time
- First deployment takes 2-3 minutes
- You'll get a public URL like: `your-app-name.up.railway.app`

### Step 4: Access Your App

Once deployed, click the generated URL to view your soccer simulation app live!

## Automatic Deployments

✅ **Now configured!** Every time you push to the `main` branch on GitHub, Railway will automatically:
1. Detect the push
2. Pull the latest code
3. Rebuild the app
4. Deploy the new version

No manual intervention needed!

## Monitoring & Management

### View Logs
- Go to your Railway project dashboard
- Click on the "Deployments" tab
- Select any deployment to view logs

### Environment Variables
If you need to add environment variables:
1. Go to your project dashboard
2. Click "Variables" tab
3. Add any needed variables

### Database Note
⚠️ **Important**: Railway's filesystem is ephemeral. Your `soccer_sim.db` SQLite file will be reset on each deployment.

For persistent data, you have two options:
1. **Railway PostgreSQL** (recommended): Add a PostgreSQL database from Railway's services
2. **External database**: Connect to an external database service

Would you like help converting to PostgreSQL for persistent storage?

## Troubleshooting

### Build Fails
- Check the build logs in Railway dashboard
- Ensure all dependencies in `requirements.txt` are correct
- Verify Python version compatibility

### App Won't Start
- Check the deployment logs
- Ensure `Procfile` is correct: `web: gunicorn app:app`
- Verify `gunicorn` is in `requirements.txt`

### Port Issues
- Railway automatically sets the `PORT` environment variable
- The app is configured to use this automatically
- No manual configuration needed

## Local Testing

You can still run locally with:

```bash
python app.py
```

The app will use port 5000 locally and Railway's PORT when deployed.

## Cost

Railway offers:
- **Free tier**: $5 of usage credit per month (enough for development/testing)
- **Hobby plan**: $5/month for more resources
- Pay-as-you-go for additional usage

## Support

- Railway docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub issues: Create issues in your repo

---

**Ready to deploy?** Follow Step 1 above to push to GitHub, then Steps 2-4 to deploy on Railway!

