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
        authenticateWithBiometrics()
    }

    private func authenticateWithBiometrics() {
        // Get the local authentication context:
        let context = LAContext()
        var error : NSError?
        
        // Test if TouchID fingerprint authentication is available on the device and a fingerprint has been enrolled.
        if context.canEvaluatePolicy(LAPolicy.DeviceOwnerAuthenticationWithBiometrics, error: &error) {
            // evaluate
            let reason = "Authenticate locally to continue"

            context.evaluatePolicy(LAPolicy.DeviceOwnerAuthenticationWithBiometrics, localizedReason: reason, reply: {
                (success: Bool, authenticationError: NSError?) -> Void in
                
                if !success {
                    _ = self.authenticationFailureReason(authenticationError)
                }
            })
        } else {
            _ = authenticationFailureReason(error)
        }
    }

    private func authenticationFailureReason(error: NSError?) -> String {
        guard let code = error?.code else {
            return "unable to authenticate user"
        }

        switch code {
        case LAError.AuthenticationFailed.rawValue:
            return "authentication failed"
        case LAError.UserCancel.rawValue:
            return "user canceled authentication"
        case LAError.SystemCancel.rawValue:
            return "system canceled authentication"
        case LAError.PasscodeNotSet.rawValue:
            return "passcode not set"
        case LAError.UserFallback.rawValue:
            return "user chose password"
        default:
            return "unable to authenticate user"
        }
    }

    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }


}
