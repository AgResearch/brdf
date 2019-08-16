--
-- Name: labresourcelist; Type: ACL; Schema: public; Owner: agrbrdf
--

REVOKE ALL ON TABLE labresourcelist FROM PUBLIC;
REVOKE ALL ON TABLE labresourcelist FROM agrbrdf;
GRANT ALL ON TABLE labresourcelist TO agrbrdf;
GRANT SELECT ON TABLE labresourcelist TO gbs;


