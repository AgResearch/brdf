--
-- Name: securityfunction; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE securityfunction FROM PUBLIC;
REVOKE ALL ON TABLE securityfunction FROM agrbrdf;
GRANT ALL ON TABLE securityfunction TO agrbrdf;
GRANT SELECT ON TABLE securityfunction TO gbs;


