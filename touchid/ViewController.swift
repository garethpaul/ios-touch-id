//
//  ViewController.swift
//  touchid
//
//  Created by Gareth on 5/23/15.
//  Copyright (c) 2015 GarethPaul. All rights reserved.
//

import UIKit
import LocalAuthentication

class ViewController: UIViewController {
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        // Get the local authentication context:
        let context = LAContext()
        var error : NSError?
        
        // Test if TouchID fingerprint authentication is available on the device and a fingerprint has been enrolled.
        do {
            if context.canEvaluatePolicy(LAPolicy.DeviceOwnerAuthenticationWithBiometrics, error: &error) {
                // evaluate
                let reason = "Authenticate for server login"
                
                context.evaluatePolicy(LAPolicy.DeviceOwnerAuthenticationWithBiometrics, localizedReason: reason, reply: {
                    (success: Bool, authenticationError: NSError?) -> Void in
                    
                    // check whether evaluation of fingerprint was successful
                    if success {
                        // fingerprint validation was successful
                        print("Fingerprint validated.")
                        
                    } else {
                        // fingerprint validation failed
                        // get the reason for validation failure
                        var failureReason = "unable to authenticate user"
                        switch error!.code {
                        case LAError.AuthenticationFailed.rawValue:
                            failureReason = "authentication failed"
                        case LAError.UserCancel.rawValue:
                            failureReason = "user canceled authentication"
                        case LAError.SystemCancel.rawValue:
                            failureReason = "system canceled authentication"
                        case LAError.PasscodeNotSet.rawValue:
                            failureReason = "passcode not set"
                        case LAError.UserFallback.rawValue:
                            failureReason = "user chose password"
                        default:
                            failureReason = "unable to authenticate user"
                        }
                        
                        print("Fingerprint validation failed: \(failureReason).");
                    }
                })
            }
        }
        // Do any additional setup after loading the view, typically from a nib.
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


}

