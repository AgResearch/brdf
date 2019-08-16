--
-- Name: oblistfact; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE oblistfact FROM PUBLIC;
REVOKE ALL ON TABLE oblistfact FROM agrbrdf;
GRANT ALL ON TABLE oblistfact TO agrbrdf;
GRANT SELECT ON TABLE oblistfact TO gbs;


