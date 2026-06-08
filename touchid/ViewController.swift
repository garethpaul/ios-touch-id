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

    private let authenticateButton = UIButton(type: UIButtonType.System)
    private var authenticationInProgress = false
    private var authenticationMessage = "authentication not started"
    
    override func viewDidLoad() {
        super.viewDidLoad()
        configureAuthenticationButton()
    }

    private func configureAuthenticationButton() {
        authenticateButton.setTitle("Authenticate Locally", forState: UIControlState.Normal)
        authenticateButton.addTarget(self, action: "authenticateButtonTapped:", forControlEvents: UIControlEvents.TouchUpInside)
        authenticateButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(authenticateButton)

        view.addConstraint(NSLayoutConstraint(
            item: authenticateButton,
            attribute: NSLayoutAttribute.CenterX,
            relatedBy: NSLayoutRelation.Equal,
            toItem: view,
            attribute: NSLayoutAttribute.CenterX,
            multiplier: 1.0,
            constant: 0.0))
        view.addConstraint(NSLayoutConstraint(
            item: authenticateButton,
            attribute: NSLayoutAttribute.CenterY,
            relatedBy: NSLayoutRelation.Equal,
            toItem: view,
            attribute: NSLayoutAttribute.CenterY,
            multiplier: 1.0,
            constant: 0.0))
    }

    @IBAction func authenticateButtonTapped(sender: AnyObject) {
        authenticateWithBiometrics()
    }

    private func authenticateWithBiometrics() {
        if authenticationInProgress {
            return
        }

        authenticationInProgress = true
        authenticationMessage = "authentication started"
        authenticateButton.enabled = false

        // Get the local authentication context:
        let context = LAContext()
        var error : NSError?
        
        // Test if TouchID fingerprint authentication is available on the device and a fingerprint has been enrolled.
        if context.canEvaluatePolicy(LAPolicy.DeviceOwnerAuthenticationWithBiometrics, error: &error) {
            // evaluate
            let reason = "Authenticate locally to continue"

            context.evaluatePolicy(LAPolicy.DeviceOwnerAuthenticationWithBiometrics, localizedReason: reason, reply: { [weak self]
                (success: Bool, authenticationError: NSError?) -> Void in
                
                dispatch_async(dispatch_get_main_queue()) {
                    self?.authenticationInProgress = false
                    self?.authenticateButton.enabled = true
                    if success {
                        self?.authenticationMessage = "authentication succeeded"
                    } else {
                        self?.authenticationMessage = self?.authenticationFailureReason(authenticationError) ?? "unable to authenticate user"
                    }
                }
            })
        } else {
            authenticationInProgress = false
            authenticateButton.enabled = true
            authenticationMessage = authenticationFailureReason(error)
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
