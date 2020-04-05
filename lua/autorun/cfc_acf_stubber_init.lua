AddCSLuaFile()
require( "cfclogger" )

local logger = CFCLogger( "ACF Stubber" )

-- Load our stubs
local PATH = "cfc_acf_stubber/stubs/"
local stubData = {}

-- In case "DATA" already exists, take copy of it to return after
local oldDATA = DATA
-- Grab folders (each named by class)
local _, classes = file.Find( PATH .. "*", "LUA" )
for _, class in pairs( classes ) do
    -- Full path of class
    local classPath = PATH .. class .. "/"
    -- Grab files within class (stubs)
    local stubs, _ = file.Find( classPath .. "*", "LUA" )
    for _, stub in pairs( stubs ) do
        -- For each stub, include it
        include( classPath .. stub )

        -- Grab its gunName from the file name (by removing .lua)
        local gunName = string.sub( stub, 1, #stub - 4 )

        stubData[gunName] = DATA
    end
end
DATA = oldDATA

local function acfIsLoaded()
    -- Acf uses gmod's "list" lib, puts the whole table of guns into it when finished loading them
    return list.HasEntry( "ACFEnts", "Guns" )
end

-- only overwrite if not already the same, don't just always set at key. ACF likely uses mt, we want to avoid bringing stuff into the foretable if not needed
local function sensitiveMerge( a, b )
    for k, v in pairs( b ) do
        if istable( a[k] ) and istable( v ) then
            sensitiveMerge( a[k], v )
        elseif a[k] ~= v then
            a[k] = v
        end
    end
end

local function mapCase( tab )
    local out = {}
    for k, v in pairs( tab ) do
        out[string.lower(v)] = v
    end
    return out
end

local function runStubs()
    logger:info( "Running stubs!" )
    local acfGuns = list.GetForEdit( "ACFEnts" ).Guns

    local lowerToNormal = mapCase( table.GetKeys( acfGuns ) )
    -- File name is converted to lower case when running AddCSLuaFile

    for gunID, gunData in pairs( stubData ) do
        gunID = lowerToNormal[gunID] or gunID
        local gun = acfGuns[gunID]
        if gun then
            if gunData.enabled then
                gunData.enabled = nil
                sensitiveMerge( gun, gunData )
            else
                acfGuns[gunID] = nil
            end
        else
            -- Could have already been removed this session
            if gunData.enabled then
                logger:info( "Found stub for gun that doesn't exist! - " .. gunID )
            end
        end
    end
end

local function handleWaiterTimeout()
    logger:info( "Waiter timed out! Not running stubs!" )
end

local waiterLoaded = Waiter

if waiterLoaded then
    logger:info( "Waiter is loaded, registering with it!" )
    Waiter.waitFor( acfIsLoaded, runStubs, handleWaiterTimeout )
else
    logger:info( "Waiter is not loaded! Inserting our struct into the queue!" )
    WaiterQueue = WaiterQueue or {}

    local struct = {}
    struct["waitingFor"] = acfIsLoaded
    struct["onSuccess"] = runStubs
    struct["onTimeout"] = handleWaiterTimeout

    table.insert( WaiterQueue, struct )
end
