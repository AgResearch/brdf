--
-- Name: accesslink; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE accesslink FROM PUBLIC;
REVOKE ALL ON TABLE accesslink FROM agrbrdf;
GRANT ALL ON TABLE accesslink TO agrbrdf;
GRANT SELECT ON TABLE accesslink TO gbs;


