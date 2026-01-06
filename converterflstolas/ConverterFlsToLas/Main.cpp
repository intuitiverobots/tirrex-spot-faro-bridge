#include <iostream>
#include <string>
#include <fstream>
#include <sstream>

#include <standalone_api/lsstandalonecontext.h>
#include <standalone_api/lsstandaloneconfig.h>

#include <core_api/lsresult.h>
#include <core_api/lsproject.h>
#include <core_api/lsscan.h>
#include <core_api/lsprocessing.h>

using namespace SCENE_API;

// Function to read API key from file
std::string readApiKeyFromFile(const std::string& filePath) {
    std::ifstream file(filePath);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open API key file: " << filePath << std::endl;
        return "";
    }
    
    std::stringstream buffer;
    buffer << file.rdbuf();
    file.close();
    
    std::string content = buffer.str();
    
    // Find the raw string literal part (the actual key content)
    size_t start = content.find("-----BEGIN SCENE API KEY-----");
    size_t end = content.find("-----END SCENE API KEY-----");
    
    if (start != std::string::npos && end != std::string::npos) {
        end += strlen("-----END SCENE API KEY-----");
        return content.substr(start, end - start);
    }
    
    std::cerr << "Error: Could not find valid API key format in file" << std::endl;
    return "";
}

int main(int argc, char* argv[])
{
    if (argc != 3) {
        std::cout << "[Usage] ConverterFlsToLas.exe <scanPath> <scanConvertedDir>" << std::endl;
        return 1;
    }

    // context
    LSStandaloneConfig config{};
    
    std::string exePathString = argv[0];
    int exePathSlashInd = int(exePathString.find_last_of("/\\"));
    if (exePathSlashInd < 0) {
        std::cout << "error: exe path couldn't be retrieved" << std::endl;
        return 1;
    }
    std::string exeDir = exePathString.substr(0, exePathSlashInd);
    std::string apiKeyPath = exeDir + "/../_Utils/FARO SCENE API key/SDK-SC-0603251312.txt";
    
    std::string apiKeyContent = readApiKeyFromFile(apiKeyPath);
    if (apiKeyContent.empty()) {
        std::cout << "error: could not read API key from file" << std::endl;
        return 1;
    }
    
    LSString apiKey = LSString::fromCharStr(apiKeyContent.c_str());
    config.setLicenseKey(apiKey);
    LSStandaloneContext context{ config };

    // result tmp
    LSResult::Result res;


    // ### PROJECT ###
    LSString exePath = LSString::fromCharStr(exePathString.c_str());
    LSString exeDir = exePath.substr(0, exePathSlashInd);
    const char PROJECT_DIR[] = "project_converter_fls_to_las";
    LSString projectDir = exeDir + '\\' + LSString::fromCharStr(PROJECT_DIR);
    const char PROJECT_NAME[] = "converter_fls_to_las";
    LSString projectName = LSString::fromCharStr(PROJECT_NAME);
    const char PROJECT_EXTENSION[] = ".lsproj";
    LSString projectExtension = LSString::fromCharStr(PROJECT_EXTENSION);
    LSString projectPath = projectDir + '\\' + projectName + projectExtension;

    // load project
    ref_ptr<LSProject> project;
    res = LSProject::loadProject(projectPath, project);
    if (res != LSResult::Ok)
    {

        // create project
        std::cout << "info: creating project..." << std::endl;
        res = LSProject::createProject(projectDir, projectName);
        if (res != LSResult::Ok)
        {
            std::cout << "error: project couldn't be created" << std::endl;
            return 1;
        }

        // load project
        res = LSProject::loadProject(projectPath, project);
        if (res != LSResult::Ok)
        {
            std::cout << "error: project couldn't be loaded" << std::endl;
            return 1;
        }
    }
    std::cout << "success: project loaded" << std::endl;

    // set current workspace
    res = context.setCurrentWorkspace(project);
    if (res != LSResult::Ok)
    {
        std::cout << "error: workspace couldn't be set as current" << std::endl;
        return 1;
    }


    // ### SCAN ###
    std::string scanPathString = argv[1];
    int scanPathSlashInd = int(scanPathString.find_last_of("/\\"));
    int scanPathDotInd = int(scanPathString.find_last_of('.'));
    if (scanPathDotInd <= scanPathSlashInd) {
        std::cout << "error: scan name couldn't be retrieved" << std::endl;
        return 1;
    }
    LSString scanPath = LSString::fromCharStr(scanPathString.c_str());
    LSString scanName = scanPath.substr(scanPathSlashInd + 1, scanPathDotInd - scanPathSlashInd - 1);
    LSString scanConvertedDir = LSString::fromCharStr(argv[2]);
    if (scanConvertedDir.find('/') != -1) {
        scanConvertedDir.append('/');
    }
    else {
        scanConvertedDir.append('\\');
    }
    const char SCAN_CONVERTED_EXTENSION[] = ".las";
    LSString scanConvertedExtension = LSString::fromCharStr(SCAN_CONVERTED_EXTENSION);
    LSString scanConvertedPath = scanConvertedDir + scanName + scanConvertedExtension;

    // import scan
    if (!project->importData(scanPath)) {
        std::cout << "error: scan couldn't be imported" << std::endl;
        return 1;
    }

    // get scans from project
    std::vector<ref_ptr<LSScan> > scans = project->getScans().get();
    if (scans.size() < 1) {
        std::cout << "error: project has no scan" << std::endl;
        return 1;
    }

    // get first (and single) scan
    ref_ptr<LSScan> scan = scans.at(0);

    // check if color is already available
    if (scan->dataAvailable(LSScan::DataFormat::COLOR)) {
        std::cout << "info: scan data already available in COLOR" << std::endl;
    }
    else {

        // load data
        res = scan->loadData();
        if (res != LSResult::Ok)
        {
            std::cout << "error: scan couldn't be loaded" << std::endl;
            return 1;
        }

        // check if data is loaded
        if (!scan->dataLoaded()) {
            std::cout << "error: scan data isn't loaded" << std::endl;
            return 1;
        }

        // process the scan
        std::cout << "info: processing scan..." << std::endl;
        res = processScan(*scan);
        if (res != LSResult::Ok)
        {
            std::cout << "error: scan couldn't be processed" << std::endl;
            return 1;
        }

        std::cout << "success: scan processed" << std::endl;
    }

    // check if data is available
    if (!scan->dataAvailable()) {
        std::cout << "error: scan data isn't available" << std::endl;
        return 1;
    }

    // load data
    res = scan->loadData();
    if (res != LSResult::Ok)
    {
        std::cout << "error: scan couldn't be loaded" << std::endl;
        return 1;
    }

    // check if data is loaded
    if (!scan->dataLoaded()) {
        std::cout << "error: scan data isn't loaded" << std::endl;
        return 1;
    }

    // exporting
    std::cout << "info: exporting scan..." << std::endl;
    res = scan->exportData(scanConvertedPath, LSScan::ExportFormat::LAS);
    if (res != LSResult::Ok)
    {
        std::cout << "error: scan couldn't be exported" << std::endl;
        return 1;
    }

    std::cout << "success: scan exported at '" << scanConvertedPath.toCharStr() << "'" << std::endl;

    return 0;
}