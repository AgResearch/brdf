--
-- Name: listmembershipfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE listmembershipfact FROM PUBLIC;
REVOKE ALL ON TABLE listmembershipfact FROM agrbrdf;
GRANT ALL ON TABLE listmembershipfact TO agrbrdf;
GRANT SELECT ON TABLE listmembershipfact TO gbs;


